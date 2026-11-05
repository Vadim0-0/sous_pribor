import logging

from fastapi import APIRouter, HTTPException, Query

from ..schemas import (
  ProductInput,
  GeneratedCard,
  FeedProduct,
  FeedGenerateRequest,
)
from ..services.card_generator import generate_card
from ..services.feed import search_products, get_product_by_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cards", tags=["Product Cards"])


@router.post("/generate", response_model=GeneratedCard)
async def generate_single_card(product: ProductInput):
  """ Генерация карточки из ручного JSON """
  try:
    return await generate_card(product)
  except RuntimeError as exc:
    raise HTTPException(status_code=502, detail=str(exc)) from exc
  except Exception as exc:
    raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/feed/search", response_model=list[FeedProduct])
async def search_products_in_feed(
  q: str = Query(..., min_length=2, max_length=200),
  limit: int = Query(20, ge=1, le=100),
):
  """ Поиск в YML-фиде из PRODUCT_DATA_URL по названию, артикулу, коду, производителю и id """

  query = q.strip()
  if len(query) < 2:
    raise HTTPException(status_code=422, detail="Введите минимум 2 символа для поиска.")

  try:
    return await search_products(query=query, limit=limit)
  except RuntimeError as exc:
    raise HTTPException(status_code=502, detail=str(exc)) from exc
  except Exception as exc:
    logger.exception("Feed search failed")
    raise HTTPException(status_code=500, detail="Внутренняя ошибка сервиса") from exc


@router.post("/feed/generate", response_model=GeneratedCard)
async def generate_card_from_selected_feed_product(payload: FeedGenerateRequest):
  """ Генерация карточки для выбранного товара из фида """
  try:
    product = await get_product_by_id(payload.product_id)
  except LookupError as exc:
    raise HTTPException(status_code=404, detail=str(exc)) from exc
  except RuntimeError as exc:
    raise HTTPException(status_code=502, detail=str(exc)) from exc

  try:
    return await generate_card(product)
  except ValueError as exc:
    raise HTTPException(status_code=503, detail=str(exc)) from exc
  except RuntimeError as exc:
    raise HTTPException(status_code=502, detail=str(exc)) from exc
  except Exception as exc:
    logger.exception("Card generation failed")
    raise HTTPException(status_code=500, detail="Внутренняя ошибка сервиса") from exc