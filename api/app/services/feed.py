import asyncio
import hashlib
import logging
import time
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from ..config import settings
from ..schemas import FeedProduct

logger = logging.getLogger(__name__)

_feed_cache: list[FeedProduct] | None = None
_feed_cache_time: float = 0
_feed_lock = asyncio.Lock()


def _local_name(tag: str) -> str:
  return tag.rsplit("}", 1)[-1]


def _find_child(element: ET.Element, name: str) -> ET.Element | None:
  for child in element:
    if _local_name(child.tag) == name:
      return child
  return None


def _find_children(element: ET.Element, name: str) -> list[ET.Element]:
  return [
    child
    for child in element
    if _local_name(child.tag) == name
  ]


def _get_text(element: ET.Element | None, default: str = "") -> str:
  if element is None:
    return default

  text = "".join(element.itertext()).strip()
  return text or default


def _child_text(
  element: ET.Element,
  child_name: str,
  default: str = "",
) -> str:
  child = _find_child(element, child_name)
  return _get_text(child, default)


def _normalize_text(value: str) -> str:
  return (
    value
    .lower()
    .replace("ё", "е")
    .strip()
  )


def _make_stable_id(offer: ET.Element, name: str, manufacturer: str) -> str:
  url = _child_text(offer, "url")
  raw = f"{name}|{manufacturer}|{url}"
  return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _parse_specs(offer: ET.Element) -> dict[str, Any]:
  specs: dict[str, Any] = {}

  for param in _find_children(offer, "param"):
    param_name = param.get("name")
    if not param_name:
      continue

    value = _get_text(param)
    unit = param.get("unit")

    if value and unit and unit not in value:
      value = f"{value} {unit}"

    if value:
      specs[param_name] = value

  return specs


def _parse_yml_feed(xml_content: bytes) -> list[FeedProduct]:
  try:
    root = ET.fromstring(xml_content)
  except ET.ParseError as exc:
    logger.exception("Failed to parse YML feed")
    raise RuntimeError("Не удалось разобрать XML-фид") from exc

  products: list[FeedProduct] = []

  for offer in root.iter():
    if _local_name(offer.tag) != "offer":
      continue

    name = _child_text(offer, "name")
    model = _child_text(offer, "model")
    type_prefix = _child_text(offer, "typePrefix")
    vendor = _child_text(offer, "vendor")
    description = _child_text(offer, "description")
    url = _child_text(offer, "url")
    picture = _child_text(offer, "picture")
    price = _child_text(offer, "price")
    currency_id = _child_text(offer, "currencyId")
    vendor_code = _child_text(offer, "vendorCode")

    if not name:
      name = model

    if type_prefix and _normalize_text(type_prefix) not in _normalize_text(name):
      name = f"{type_prefix} {name}".strip()

    if not name:
      continue

    product_id = offer.get("id") or _make_stable_id(
      offer=offer,
      name=name,
      manufacturer=vendor,
    )

    specs = _parse_specs(offer)

    vendor_code = _child_text(offer, "vendorCode") or str(specs.pop("Артикул", "") or "")
    raw_product_code = specs.pop("Код товара", None)
    product_code = str(raw_product_code).strip() if raw_product_code else ""

    products.append(
      FeedProduct(
        id=product_id,
        name=name,
        manufacturer=vendor or None,
        vendor_code=vendor_code or None,
        product_code=product_code or None,
        specs=specs,
        description=description or None,
        url=url or None,
        picture=picture or None,
        price=price or None,
        currency=currency_id or None,
      )
    )

  logger.info("Parsed %s products from YML feed", len(products))
  return products


async def load_feed_products(force_refresh: bool = False) -> list[FeedProduct]:
  """ скачивает фид и 10 минут отдаёт его из памяти. """

  global _feed_cache, _feed_cache_time

  now = time.monotonic()

  if (
    not force_refresh
    and _feed_cache is not None
    and now - _feed_cache_time < settings.feed_cache_ttl_seconds
  ):
    return _feed_cache

  async with _feed_lock:
    now = time.monotonic()

    if (
      not force_refresh
      and _feed_cache is not None
      and now - _feed_cache_time < settings.feed_cache_ttl_seconds
    ):
      return _feed_cache

    logger.info("Loading product feed: %s", settings.product_data_url)

    try:
      async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers={
          "User-Agent": "ProductCardGenerator/1.0",
        },
      ) as client:
        response = await client.get(settings.product_data_url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
      logger.exception("Failed to load YML feed")
      raise RuntimeError("Не удалось загрузить YML-фид") from exc

    products = _parse_yml_feed(response.content)

    _feed_cache = products
    _feed_cache_time = time.monotonic()

    return products


async def search_products(query: str, limit: int = 20) -> list[FeedProduct]:
  """ ищет по названию, артикулу, коду, производителю и id, не больше limit штук. """

  products = await load_feed_products()

  normalized_query = _normalize_text(query)
  tokens = normalized_query.split()

  if not tokens:
    return []

  result: list[FeedProduct] = []

  for product in products:
    product_code = product.specs.get("Код товара", "")
    haystack = _normalize_text(" ".join(
      part for part in (
        product.name,
        product.vendor_code or "",
        product.product_code or "",
        product.manufacturer or "",
        product.id,
        str(product_code),
      )
      if part
    ))

    if all(token in haystack for token in tokens):
      result.append(product)

      if len(result) >= limit:
        break

  return result


async def get_product_by_id(product_id: str) -> FeedProduct:
  """ возвращает товар для генерации или ошибку, если id нет """

  products = await load_feed_products()

  for product in products:
    if product.id == product_id:
      return product

  raise LookupError(f"Товар с id={product_id} не найден")