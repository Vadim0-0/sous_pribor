import httpx
import json
import logging

from pydantic import ValidationError

from ..config import settings
from ..schemas import ProductInput, GeneratedCard

logger = logging.getLogger(__name__)

async def generate_card(product: ProductInput) -> GeneratedCard:
  if not settings.ai_enabled:
    raise ValueError("AI generation is disabled in settings")

  prompt = f"""
    Ты эксперт по SEO и техническому копирайтингу для B2B-оборудования. 
    Сформируй карточку товара на основе следующих данных:
    - Название: {product.name}
    - Производитель: {product.manufacturer or 'Не указан'}
    - Артикул: {product.vendor_code or "Не указан"}
    - Код товара: {product.product_code or "Не указан"}
    - Характеристики: {json.dumps(product.specs, ensure_ascii=False, indent=2)}
    - Описание: {product.description or 'Не указано'}

    Ты должен вернуть СТРОГО валидный JSON со следующей структурой:
    {{
      "seo_title": "SEO заголовок до 70 символов",
      "seo_description": "Подробное SEO описание. Напиши 3-4 развернутых абзаца, раскрывая преимущества, применение и технические детали, чтобы достичь объема 800-1200 символов.",
      "key_characteristics": ["Характеристика 1: значение", "Характеристика 2: значение"],
      "search_queries": ["запрос 1", "запрос 2", "запрос 3", "запрос 4"],
      "commercial_block": "Краткий блок для менеджера: кому подходит прибор и какие конкретные задачи решает. 2-3 предложения.",
      "missing_data": [
        {{"field": "название отсутствующего поля", "reason": "почему это важно и что нужно уточнить"}}
      ]
    }}
    
    Правила:
    1. Если критически важных данных не хватает, добавь их в массив missing_data.
    2. Возвращай ТОЛЬКО чистый JSON, без пояснений и без markdown-обертки ```json.
    3. Язык ответа: русский,
    4. Пиши грамматически верно: согласовывай род и падеж. Правильно: «точное измерение», не «точную измерение».
  """

  ollama_url = f"{settings.ai_base_url}/api/chat"
  
  payload = {
    "model": settings.ai_model,
    "messages": [
      {
        "role": "system", 
        "content": "Ты строгий JSON-генератор. Ты никогда не добавляешь markdown-обертки и возвращаешь только валидный JSON."
      },
      {
        "role": "user", 
        "content": prompt
      }
    ],
    "stream": False,
    "format": "json",
    "options": {
      "temperature": 0.2,
      "num_predict": 2000
    }
  }
  
  logger.info(f"Sending request to Ollama for product: {product.name}")
  content: str | None = None
  async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
    try:
      response = await client.post(ollama_url, json=payload)
      response.raise_for_status()
      result = response.json()

      message = result.get("message") if isinstance(result, dict) else None
      raw_content = message.get("content") if isinstance(message, dict) else None
      if not isinstance(raw_content, str):
        raise RuntimeError("LLM вернула ответ без текста")

      content = raw_content.replace("```json", "").replace("```", "").strip()
      data = json.loads(content)
      return GeneratedCard.model_validate(data)

    except httpx.HTTPError as e:
      logger.error("Ollama request failed: %s", e)
      raise RuntimeError(f"Ошибка при обращении к LLM: {e}") from e

    except json.JSONDecodeError as e:
      logger.error("Failed to parse LLM response. Raw: %s", content)
      raise RuntimeError(f"LLM вернула невалидный JSON: {e}") from e

    except ValidationError as e:
      logger.error("LLM JSON does not match schema: %s", e)
      raise RuntimeError(f"LLM вернула JSON неверной структуры: {e}") from e

    except RuntimeError:
      raise