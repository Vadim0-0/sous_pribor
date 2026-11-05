import type { FeedProduct } from '~/types/cards'

export function useFeedSearch() {
  const searchQuery = ref('');
  const products = ref<FeedProduct[]>([]);
  const isSearching = ref(false);
  const hasSearched = ref(false);
  const searchError = ref('');

  async function searchFeedProducts(): Promise<void> {
    if (isSearching.value) {
      return
    };

    const query = searchQuery.value.trim();

    products.value = [];
    searchError.value = '';

    if (query.length < 2) {
      hasSearched.value = false;
      searchError.value = 'Введите минимум 2 символа для поиска.';
      return;
    };

    isSearching.value = true;
    hasSearched.value = true;

    try {
      products.value = await $fetch<FeedProduct[]>('/api/cards/feed/search', {
        query: {
          q: query,
        },
      });
    } catch (error: unknown) {
      searchError.value = `Ошибка поиска: ${getErrorMessage(error)}`;
    } finally {
      isSearching.value = false;
    };
  };

  function clearSearch(): void {
    searchQuery.value = '';
    products.value = [];
    searchError.value = '';
    hasSearched.value = false;
  };

  return {
    searchQuery,
    products,
    isSearching,
    hasSearched,
    searchError,
    searchFeedProducts,
    clearSearch,
  };
};