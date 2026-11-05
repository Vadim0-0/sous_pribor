import type {ProductInput } from '~/types/cards';
import { translateKeys } from '~/utils/translateKeys';

function parseProductInput(raw: string): ProductInput {
  const parsed: unknown = JSON.parse(raw);

  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    throw new Error('Ошибка: JSON должен быть объектом товара.')
  };

  const data = parsed as Record<string, unknown>;

  if (typeof data.name !== 'string' || data.name.trim().length === 0) {
    throw new Error('Ошибка: у товара должно быть непустое поле name.')
  };

  if (
    typeof data.specs !== 'object'
    || data.specs === null
    || Array.isArray(data.specs)
  ) {
    throw new Error('Ошибка: specs должен быть объектом характеристик.')
  };

  const specs: Record<string, string> = {};

  for (const [key, value] of Object.entries(data.specs)) {
    specs[key] = typeof value === 'string' ? value : String(value)
  };

  return {
    name: data.name.trim(),
    manufacturer: typeof data.manufacturer === 'string' ? data.manufacturer : null,
    specs,
    description: typeof data.description === 'string' ? data.description : null,
  };
}

export function useCardGenerator() {
  const defaultProduct: ProductInput = {
    name: 'Манометр показывающий DM 02',
    manufacturer: 'Манотомь',
    specs: {
      'диапазон измерений': '0–1,6 МПа',
      'класс точности': '1,5',
      'присоединение': 'G1/2',
      'диаметр корпуса': '100 мм',
    },
    description: 'Прибор предназначен для измерения избыточного давления.',
  }

  const jsonInput = ref(JSON.stringify(defaultProduct, null, 2));

  const resultText = ref(
    'Выберите товар из фида или отправьте JSON вручную.',
  );
  const isResultError = ref(false);
  const isGenerating = ref(false);
  const activeProductId = ref<string | null>(null);

  async function generateSelectedProduct(productId: string): Promise<void> {
    if (isGenerating.value) {
      return
    }

    isGenerating.value = true
    activeProductId.value = productId
    isResultError.value = false
    resultText.value = 'Товар выбран. Идёт генерация карточки через LLM...'

    try {
      const card = await $fetch('/api/cards/feed/generate', {
        method: 'POST',
        body: {
          product_id: productId,
        },
      })

      resultText.value = JSON.stringify(translateKeys(card), null, 2)
    } catch (error: unknown) {
      isResultError.value = true
      resultText.value = `Ошибка генерации: ${getErrorMessage(error)}`
    } finally {
      isGenerating.value = false
      activeProductId.value = null
    }
  };

  async function generateFromJson(): Promise<void> {
    if (isGenerating.value) {
      return
    }

    let product: ProductInput

    try {
      product = parseProductInput(jsonInput.value)
    } catch (error: unknown) {
      isResultError.value = true
      resultText.value = error instanceof Error
        ? error.message
        : 'Ошибка: введён невалидный JSON.'
      return
    }

    isGenerating.value = true
    activeProductId.value = null
    isResultError.value = false
    resultText.value = 'Идёт генерация карточки через LLM'

    try {
      const card = await $fetch<GeneratedCard>(
        '/api/cards/generate',
        {
          method: 'POST',
          body: product,
        },
      )

      resultText.value = JSON.stringify(translateKeys(card), null, 2)
    } catch (error: unknown) {
      isResultError.value = true
      resultText.value = `Ошибка генерации: ${getErrorMessage(error)}`
    } finally {
      isGenerating.value = false
    }
  };

  function clearJson(): void {
    jsonInput.value = ''
  };

  return {
    jsonInput,
    resultText,
    isResultError,
    isGenerating,
    activeProductId,
    generateSelectedProduct,
    generateFromJson,
    clearJson,
  };
};