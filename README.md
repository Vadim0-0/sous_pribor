# Генератор SEO-карточек

Сервис ищет товар в YML-фиде «Союз-прибор» или принимает JSON вручную и просит локальную модель Ollama собрать SEO-карточку: заголовок, описание, характеристики, поисковые запросы и блок для менеджера.

Интерфейс — Nuxt (`web`). Данные и генерация — FastAPI (`api`). Перед сайтом стоит Nginx.

## Запуск

Нужны Docker, Make и файл `.env` в корне. Его можно скопировать из примера:

```bash
cp .env.example .env
```

В `.env` обязателен `PRODUCT_DATA_URL` — адрес YML-фида. Модель по умолчанию `qwen2.5:3b`.

Команды запуска собраны в `Makefile`. С логами в терминале:

```bash
make up
```

В фоне:

```bash
make up-d
```

Оба варианта поднимают Docker Compose с файлом разработки: API и фронт перезагружаются при правках кода.

- интерфейс: http://localhost:3000
- сайт через Nginx: http://localhost
- API: http://localhost:8000
- проверка API: http://localhost:8000/health

Первый старт долгий: сервис `ollama-init` скачивает модель. Ход загрузки — `make logs-init`.

Остальные команды: `make logs` смотрит логи, `make ps` показывает контейнеры, `make restart` перезапускает их без пересборки, `make down` останавливает.

## API

`api/app/main.py` — приложение FastAPI и роутер карточек. `health_check` отвечает, что сервис жив.

`api/app/config.py` — настройки из `.env`. `get_settings` читает их один раз: адрес фида, модель, таймаут и время кэша фида.

`api/app/schemas.py` — формы данных. `ProductInput` — товар для генерации. `FeedProduct` добавляет id оффера, ссылку, фото и цену. `FeedGenerateRequest` — id выбранного товара. `GeneratedCard` и `MissingData` — ответ модели.

`api/app/routers/product_cards.py`

- `search_products_in_feed` — `GET /api/cards/feed/search`, поиск по фиду.
- `generate_single_card` — `POST /api/cards/generate`, карточка из JSON.
- `generate_card_from_selected_feed_product` — `POST /api/cards/feed/generate`, карточка товара из фида.

`api/app/services/feed.py` — загрузка и разбор YML. Вспомогательные функции снимают namespace с тегов, читают текст, характеристики и артикул. Если у оффера нет id, `_make_stable_id` делает его из названия, производителя и ссылки.

- `load_feed_products` — скачивает фид и держит его в памяти 10 минут.
- `search_products` — ищет по названию, артикулу, коду, производителю и id. По умолчанию не больше 20 позиций.
- `get_product_by_id` — находит товар для генерации.

`api/app/services/card_generator.py` — `generate_card` отправляет данные товара в Ollama и проверяет, что ответ совпал со схемой карточки.

## Web

`web/app/pages/index.vue` — страница поиска, ручного JSON и результата.

`web/app/types/cards.ts` — те же типы товара и карточки, что у API.

`web/app/composables/useFeedSearch.ts` — `searchFeedProducts` запрашивает поиск, `clearSearch` очищает запрос и список.

`web/app/composables/useCardGenerator.ts` — `parseProductInput` проверяет ручной JSON. `generateSelectedProduct` генерирует карточку выбранного товара, `generateFromJson` — из текста в поле, `clearJson` очищает поле.

`web/app/utils/errors.ts` — `getErrorMessage` достаёт текст ошибки API. `web/app/utils/translateKeys.ts` — `translateKeys` переводит ключи карточки на русский перед показом. `web/app/utils/text.ts` — `truncateText` обрезает описание в списке.

`web/app/components/ui/uiButton/UiButton.vue` — общая кнопка. `web/nuxt.config.ts` проксирует запросы `/api` на FastAPI.
