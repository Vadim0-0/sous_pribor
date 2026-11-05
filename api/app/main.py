from fastapi import FastAPI

from .routers import product_cards

app = FastAPI(
  title="Product Card Generator API",
  description="Сервис для генерации SEO-карточек товаров с помощью LLM",
  version="1.0.0"
)

app.include_router(product_cards.router)

@app.get("/health")
def health_check():
  return {"status": "ok", "service": "product-card-generator"}
