const FIELD_TRANSLATIONS: Record<string, string> = {
  seo_title: 'SEO заголовок',
  seo_description: 'SEO описание',
  key_characteristics: 'Ключевые характеристики',
  search_queries: 'Поисковые запросы',
  commercial_block: 'Коммерческий блок',
  missing_data: 'Недостающие данные',
  field: 'Поле',
  reason: 'Причина',
};

export function translateKeys(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(item => translateKeys(item))
  };

  if (typeof value !== 'object' || value === null) {
    return value
  };

  const translated: Record<string, unknown> = {};

  for (const [key, nestedValue] of Object.entries(value)) {
    const translatedKey = FIELD_TRANSLATIONS[key] ?? key;
    translated[translatedKey] = translateKeys(nestedValue);
  };

  return translated;
};