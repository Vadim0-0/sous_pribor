<script setup lang="ts">
  useHead({
    title: 'Генератор SEO-карточек товаров',
 })

  const {
    searchQuery,
    products,
    isSearching,
    hasSearched,
    searchError,
    searchFeedProducts,
    clearSearch,
  } = useFeedSearch()

  const {
    jsonInput,
    resultText,
    isResultError,
    isGenerating,
    activeProductId,
    generateSelectedProduct,
    generateFromJson,
    clearJson,
  } = useCardGenerator()
</script>

<template>
  <section class="index">
    <div class="container">
      <div class="index__content">

        <div class="index__content-scroll">
          
          <div class="index__content-folders">
  
            <div class="index__content-folders__block">
  
              <div class="index__content-folders__block-info">
  
                <div class="index__content-folders__block-info__title">
                  <h2>
                    Вариант 1: Найти товар в фиде
                  </h2>
                </div>
  
                <div class="index__content-folders__block-info__descr">
                  <p>
                    Введите часть названия товара. Сервис найдёт подходящие позиции, а затем вы сможете выбрать нужную.
                  </p>
                </div>  
              </div>
  
              <div class="index__content-folders__block-search">
  
                <label for="feedSearchInput" class="search-label">
                  <p>
                    Поиск
                  </p>
                  <input
                    id="feedSearchInput"
                    v-model="searchQuery"
                    type="text"
                    placeholder="Например: манометр, DM 02, термометр"
                    @keydown.enter="searchFeedProducts"
                  >
                </label>
  
              </div>
  
              <div class="index__content-folders__block-btns">
                <UiButton
                  class="index__content-folders__block-btns__btn"
                  :disabled="isSearching"
                  @click="clearSearch"
                >
                  <p>
                    Очистить
                  </p>
                </UiButton>

                <UiButton
                  class="index__content-folders__block-btns__btn"
                  :disabled="isSearching"
                  @click="searchFeedProducts"
                >
                  <p>
                    {{ isSearching ? 'Поиск...' : 'Найти' }}
                  </p>
                </UiButton>
              </div>
  
              <div class="index__content-folders__block-result">

                <div
                  v-if="isSearching"
                  class="index__content-folders__block-result__empty"
                >
                  <p>Идёт поиск товаров...</p>
                </div>

                <div
                  v-else-if="searchError"
                  class="index__content-folders__block-result__error"
                >
                  <p>{{ searchError }}</p>
                </div>

                <div
                  v-else-if="hasSearched && products.length === 0"
                  class="index__content-folders__block-result__empty"
                >
                  <p>Ничего не найдено.</p>
                </div>

                <div
                  v-else-if="!hasSearched"
                  class="index__content-folders__block-result__empty"
                >
                  <p>Введите запрос и нажмите «Найти».</p>
                </div>

                <ul v-else class="result-list">
                  <li
                    v-for="product in products"
                    :key="product.id"
                    class="result-list__item"
                  >
                    <div class="result-list__item-info">
                      <div class="result-list__item-info__img">
                        <img
                          v-if="product.picture"
                          :src="product.picture"
                          :alt="product.name"
                          loading="lazy"
                        >

                        <span class="icon" v-else>
                          <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
                            <path d="M0 0h24v24H0z" fill="none" />
                            <g fill="none">
                              <path stroke="currentColor" stroke-width="2" d="M3 11c0-3.771 0-5.657 1.172-6.828S7.229 3 11 3h2c3.771 0 5.657 0 6.828 1.172S21 7.229 21 11v2c0 3.771 0 5.657-1.172 6.828S16.771 21 13 21h-2c-3.771 0-5.657 0-6.828-1.172S3 16.771 3 13z" />
                              <path fill="currentColor" fill-rule="evenodd" d="m19 13.585l-.02-.02c-.39-.39-.726-.726-1.026-.979c-.317-.267-.662-.502-1.088-.63a3 3 0 0 0-1.732 0c-.426.129-.77.363-1.088.63c-.3.253-.636.59-1.025.98l-.029.028c-.307.306-.487.486-.628.601l-.02.017l-.012-.023c-.087-.16-.189-.393-.36-.792l-.053-.124l-.022-.052c-.356-.83-.655-1.528-.95-2.054c-.305-.541-.685-1.05-1.277-1.346a3 3 0 0 0-1.597-.307c-.66.055-1.201.386-1.685.775c-.406.327-.86.77-1.388 1.297V13q0 .774.003 1.411l1.114-1.114c.69-.69 1.15-1.147 1.525-1.45c.37-.298.53-.335.6-.34a1 1 0 0 1 .532.102c.061.031.196.124.43.54c.236.42.493 1.016.877 1.912l.053.124l.017.038c.149.348.287.67.425.924c.145.265.355.583.709.802a2 2 0 0 0 1.398.27c.41-.073.723-.29.956-.482c.222-.184.47-.432.738-.7l.03-.03c.425-.425.701-.7.928-.891c.218-.184.32-.228.376-.245a1 1 0 0 1 .578 0c.056.017.158.061.376.245c.227.191.503.466.929.892l1.35 1.35c.046-.718.054-1.61.056-2.773" clip-rule="evenodd" />
                              <circle cx="16.5" cy="7.5" r="1.5" fill="currentColor" />
                            </g>
                          </svg>
                        </span>

                      </div>
                      <div class="result-list__item-info__article">
                        <h3>
                          {{ product.name }}
                        </h3>

                        <p>
                          Артикул: <span>{{ product.vendor_code || '—' }}</span>
                        </p>
                        <p>
                          Код товара: <span>{{ product.product_code || '—' }}</span>
                        </p>
                        <p>
                          {{
                            product.description
                              ? truncateText(product.description)
                              : 'Описание отсутствует'
                          }}
                        </p>
                      </div>
                    </div>
                    <div class="result-list__item-btn">
                      <UiButton
                        :disabled="isGenerating"
                        @click="generateSelectedProduct(product.id)"
                      >
                        <p>
                          {{
                            isGenerating && activeProductId === product.id
                              ? 'Генерация...'
                              : 'Выбрать и сгенерировать'
                          }}
                        </p>
                      </UiButton>
                    </div>
                  </li>
                </ul>
  
              </div>
  
            </div>
  
            <div class="index__content-folders__block">
  
              <div class="index__content-folders__block-info">
  
                <div class="index__content-folders__block-info__title">
                  <h2>
                    Вариант 2: Ручной ввод JSON
                  </h2>
                </div>
  
                <div class="index__content-folders__block-info__descr">
                  <p>
                    Можно вручную отправить данные товара в формате JSON.
                  </p>
                </div>  
              </div>
  
              <div class="index__content-folders__block-folder">
                <textarea
                  id="jsonInput"
                  v-model="jsonInput"
                  rows="12"
                  spellcheck="false"
                ></textarea>
              </div>
  
              <div class="index__content-folders__block-btns">
                <UiButton
                  class="index__content-folders__block-btns__btn"
                  :disabled="isGenerating"
                  @click="clearJson"
                >
                  <p>
                    Очистить
                  </p>
                </UiButton>
                <UiButton
                  class="index__content-folders__block-btns__btn"
                  :disabled="isGenerating"
                  @click="generateFromJson"
                >
                  <p>
                    {{
                      isGenerating && activeProductId === null
                        ? 'Генерация...'
                        : 'Сгенерировать из JSON'
                    }}
                  </p>
                </UiButton>
              </div>
  
            </div>
  
          </div>

        </div>

        <div class="index__content-scroll">
          <div class="index__content-result">
            <div class="index__content-result__title">
              <h2>
                Результат
              </h2>
            </div>
  
            <div class="index__content-result__pre">
              <pre v-if="!isResultError" id="result">{{ resultText }}</pre>

              <div
                v-else
                class="index__content-result__pre-error"
              >
                <p>{{ resultText }}</p>
              </div>
            </div>
          </div>
        </div>
        
      </div>
    </div>
  </section>
</template>