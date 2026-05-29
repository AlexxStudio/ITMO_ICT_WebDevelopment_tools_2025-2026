# Лабораторная работа №3

## Цель работы

Изучить основы контейнеризации приложений с использованием Docker и Docker Compose, а также реализовать взаимодействие между микросервисами и асинхронную обработку задач с помощью Celery и Redis.

---

## Ход работы

### Подготовка проекта

В качестве основы был использован проект, разработанный в предыдущих лабораторных работах.

В рамках данной лабораторной работы были добавлены следующие компоненты:

- основной FastAPI-сервис (`app`);
- отдельный сервис парсинга веб-страниц (`parser_service`);
- Celery для выполнения фоновых задач;
- Redis в качестве брокера сообщений;
- Docker Compose для управления контейнерами.

Структура проекта:

```text
lr3
│
├── app
│   ├── __init__.py
│   ├── auth.py
│   ├── celery_app.py
│   ├── connection.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── tasks.py
│
├── parser_service
│   ├── main.py
│   └── requirements.txt
│
├── docker-compose.yml
├── Dockerfile.api
└── Dockerfile.parser
```

---

### Контейнеризация сервисов

Для контейнеризации были созданы отдельные Dockerfile для каждого сервиса.

#### Dockerfile основного API

```dockerfile
FROM python:3.12-slim

WORKDIR /code

COPY app/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile сервиса парсинга

```dockerfile
FROM python:3.12-slim

WORKDIR /code

COPY parser_service/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY parser_service ./parser_service

CMD ["uvicorn", "parser_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

### Настройка Docker Compose

Для запуска всех компонентов был создан файл `docker-compose.yml`.

В системе используются следующие контейнеры:

- API-сервис;
- сервис парсинга;
- PostgreSQL;
- Redis;
- Celery Worker.

После запуска были успешно подняты контейнеры:

```text
lr3_api
lr3_parser
lr3_db
lr3_redis
lr3_worker
```

---

### Реализация микросервиса парсинга

Был разработан отдельный FastAPI-сервис, который принимает URL страницы и возвращает её заголовок.

Эндпоинт сервиса:

```http
POST /parse
```

Пример ответа:

```json
{
  "title": "Welcome to Python.org"
}
```

Сервис запускается в отдельном контейнере и доступен внутри Docker-сети по имени контейнера.

---

### Интеграция микросервиса с основным API

В основном приложении были реализованы два новых эндпоинта.

#### Синхронный парсинг

```http
POST /parse
```

Алгоритм работы:

1. Пользователь отправляет URL в основной API.
2. Основной API обращается к сервису парсинга.
3. Полученный результат сохраняется в базе данных.
4. Пользователю возвращается информация о странице.

---

#### Асинхронный парсинг

```http
POST /parse-async
```

Алгоритм работы:

1. Пользователь отправляет URL.
2. Основной API создаёт задачу Celery.
3. Задача помещается в очередь Redis.
4. Celery Worker выполняет парсинг страницы.
5. Результат сохраняется в базе данных.
6. Пользователь может получить статус выполнения задачи.

---

### Использование Celery и Redis

Для реализации асинхронного выполнения задач использовались:

- Redis — брокер сообщений;
- Celery Worker — исполнитель задач.

Для проверки статуса задачи реализован эндпоинт:

```http
GET /tasks/{task_id}
```

---

## Тестирование

### Проверка синхронного парсинга

Запрос:

```http
POST /parse?url=https://python.org
```

Ответ:

```json
{
  "message": "Page parsed successfully",
  "data": {
    "id": 1,
    "url": "https://python.org",
    "title": "Welcome to Python.org"
  }
}
```

---

### Проверка асинхронного парсинга

Запрос:

```http
POST /parse-async?url=https://github.com
```

Ответ:

```json
{
  "message": "Task added to queue",
  "task_id": "7409e607-e86d-457a-80b3-bd6600786250"
}
```

После выполнения задачи был выполнен запрос:

```http
GET /tasks/7409e607-e86d-457a-80b3-bd6600786250
```

Ответ:

```json
{
  "task_id": "7409e607-e86d-457a-80b3-bd6600786250",
  "status": "SUCCESS",
  "result": {
    "id": 2,
    "url": "https://github.com",
    "title": "GitHub · Change is constant. GitHub keeps you ahead. · GitHub"
  }
}
```

---

### Проверка контейнеров

После запуска Docker Compose были успешно подняты контейнеры:

```text
lr3_api
lr3_parser
lr3_db
lr3_redis
lr3_worker
```

Все сервисы работали корректно и взаимодействовали друг с другом через внутреннюю Docker-сеть.

---

## Вывод

В ходе выполнения лабораторной работы были изучены технологии Docker, Docker Compose, Redis и Celery.

Был реализован отдельный микросервис парсинга веб-страниц, интегрированный с основным FastAPI-приложением. Также была реализована асинхронная обработка задач с использованием очереди сообщений Redis и Celery Worker.

Все сервисы были успешно контейнеризированы и объединены в единую систему с помощью Docker Compose.
