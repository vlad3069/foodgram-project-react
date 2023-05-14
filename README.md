
[![API FoodGram Project CI/CD](https://github.com/vlad3069/foodgram-project-react/actions/workflows/foodgram_workflo.yml/badge.svg)](https://github.com/vlad3069/foodgram-project-react/actions/workflows/foodgram_workflo.yml)

# Foodrgam

 Продуктовый помощник - дипломный проект курса Backend-разработки Яндекс.Практикум. Проект представляет собой онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект реализован на `Django` и `DjangoRestFramework`. Доступ к данным реализован через API-интерфейс. Документация к API написана с использованием `Redoc`.

## Особенности реализации

- Проект завернут в Docker-контейнеры;
- Образы foodgram_frontend и foodgram_backend запушены на DockerHub;
- Реализован workflow c автодеплоем на удаленный сервер и отправкой сообщения в Telegram;
- Проект был развернут на сервере: <http://130.193.48.151/recipes>

## Развертывание проекта

### Развертывание на локальном сервере

1. Установите на сервере `docker` и `docker-compose`.
2. Создайте файл `/infra/.env`.
3. Выполните команду `docker-compose up -d --buld`.
4. Создайте суперюзера `docker-compose exec backend python manage.py createsuperuser`.
5. Заполните базу ингредиентами `docker-compose exec backend python manage.py load_ingrid`.
8. **Для создания рецепта, надо создать пару тегов через админку.**
9. Документация к API находится по адресу: <http://localhost/api/docs/redoc.html>.

## Автор

[vlad9603]Владислав Подтяжкин 
