# make up 				 запуск с выводом логов
# make up-d      	 запуск в фоне
# make logs        смотреть логи
# make logs-init   смотреть загрузку модели
# make ps          состояние сервисов
# make restart     перезапуск
# make down        остановка

.PHONY: up dev down restart logs logs-init ps

.DEFAULT_GOAL := up

COMPOSE      = docker compose
COMPOSE_DEV  = $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml


# Сборка и запуск всех сервисов с выводом логов
up:
	$(COMPOSE_DEV) up --build

# Сборка и запуск всех сервисов в фоне
up-d:
	$(COMPOSE_DEV) up --build -d
	$(COMPOSE_DEV) ps

# Остановка и удаление контейнеров
down:
	$(COMPOSE_DEV) down

# Перезапуск без пересборки
restart:
	$(COMPOSE_DEV) restart

# Логи всех сервисов
logs:
	$(COMPOSE_DEV) logs -f

# Логи загрузки модели Ollama
logs-init:
	$(COMPOSE_DEV) logs -f ollama-init

# Состояние контейнеров
ps:
	$(COMPOSE_DEV) ps