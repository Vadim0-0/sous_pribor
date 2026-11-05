export interface ProductInput {
  name: string
  manufacturer: string | null
  specs: Record<string, string>
  description: string | null
};

export interface FeedProduct extends ProductInput {
  id: string
  url: string | null
  picture: string | null
  price: string | null
  currency: string | null
  vendor_code: string | null
  product_code: string | null
};

export interface MissingData {
  field: string
  reason: string
};

export interface GeneratedCard {
  seo_title: string
  seo_description: string
  key_characteristics: string[]
  search_queries: string[]
  commercial_block: string
  missing_data: MissingData[]
};