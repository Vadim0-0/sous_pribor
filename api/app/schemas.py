from typing import Any

from pydantic import BaseModel, Field


class ProductInput(BaseModel):
  name: str = Field(..., min_length=1)
  manufacturer: str | None = None
  specs: dict[str, Any] = Field(default_factory=dict)
  description: str | None = None
  vendor_code: str | None = None
  product_code: str | None = None


class FeedProduct(ProductInput):
  id: str
  url: str | None = None
  picture: str | None = None
  price: str | None = None
  currency: str | None = None


class FeedGenerateRequest(BaseModel):
  product_id: str = Field(..., min_length=1)


class MissingData(BaseModel):
  field: str
  reason: str


class GeneratedCard(BaseModel):
  seo_title: str = Field(..., max_length=70)
  seo_description: str
  key_characteristics: list[str]
  search_queries: list[str] = Field(..., min_length=3, max_length=5)
  commercial_block: str
  missing_data: list[MissingData] = Field(default_factory=list)