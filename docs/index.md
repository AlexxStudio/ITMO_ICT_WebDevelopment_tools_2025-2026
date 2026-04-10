# Лабораторная работа 1. Реализация серверного приложения FastAPI

## Студент

- ФИО: Алексей Баженов
- Группа: k3340

## Тема

Разработка сервиса для управления личными финансами.

---

## Цель работы

Реализовать серверное приложение на FastAPI с использованием SQLModel, PostgreSQL, Alembic и JWT-аутентификации.  
Обеспечить поддержку CRUD-операций, связей между сущностями и бизнес-логики.

---

## Ссылки на выполненные практики

- Практика 1.1:
  - https://github.com/AlexxStudio/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/a4b804858155300c2af059cebabe8b81f8055bd4
  - https://github.com/AlexxStudio/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/3b436294b28ef9821aae1088b4817a9fa1052afc
- Практика 1.2:
  - https://github.com/AlexxStudio/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/f57546c317643c5a86dc6f3766d5980edaae3051
- Практика 1.3:
  - https://github.com/AlexxStudio/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/d43eb50a53bfecf854d708f9018f104a37bdaf5f
  - https://github.com/AlexxStudio/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/468b45e2ce2d4b9d6c525dd5afb4ace149ebda1f

---

## Модели данных

### User

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password: str
```

### Account

```python
class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    balance: float = 0.0
    user_id: int = Field(foreign_key="user.id")
```

### Category

```python
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str
    user_id: int = Field(foreign_key="user.id")
```

### Transaction

```python
class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    description: Optional[str] = None
    date: str
    account_id: int = Field(foreign_key="account.id")
    category_id: int = Field(foreign_key="category.id")
```

### Tag

```python
class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
```

### TransactionTag

```python
class TransactionTag(SQLModel, table=True):
    transaction_id: Optional[int] = Field(default=None, foreign_key="transaction.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)
    note: Optional[str] = None
```

### Budget

```python
class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    limit_amount: float
    period: str
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
```

---

## Связи между сущностями

- User → Account (one-to-many)
- User → Category (one-to-many)
- User → Budget (one-to-many)
- Account → Transaction (one-to-many)
- Category → Transaction (one-to-many)
- Transaction ↔ Tag (many-to-many через TransactionTag)

### Ассоциативная сущность:

- TransactionTag (с дополнительным полем note)

---

## Подключение к базе данных

```python
import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
```

---

## Аутентификация

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
```

---

## Реализованные эндпоинты

### Пользователи

- POST /register
- POST /login
- GET /me
- GET /users
- GET /users/{user_id}
- PUT /users/{user_id}/change-password
- DELETE /users/{user_id}

### Accounts

- GET /accounts
- POST /accounts
- GET /accounts/{account_id}
- DELETE /accounts/{account_id}

### Categories

- GET /categories
- POST /categories
- GET /categories/{category_id}
- DELETE /categories/{category_id}

### Transactions

- GET /transactions
- POST /transactions
- GET /transactions/{transaction_id}
- DELETE /transactions/{transaction_id}
- GET /transactions/{transaction_id}/full

### Tags

- GET /tags
- POST /tags
- GET /tags/{tag_id}
- DELETE /tags/{tag_id}

### TransactionTags

- POST /transaction-tags
- GET /transaction-tags
- DELETE /transaction-tags

### Budgets

- GET /budgets
- POST /budgets
- GET /budgets/{budget_id}
- DELETE /budgets/{budget_id}

### Отчёты

- GET /report/summary/{user_id}

---

## Бизнес-логика

- При создании транзакции:
  - income увеличивает баланс счёта
  - expense уменьшает баланс
- При удалении транзакции:
  - баланс пересчитывается

---

## Вывод

В ходе лабораторной работы был реализован серверный сервис управления личными финансами с использованием FastAPI.
Реализованы CRUD-операции, связи one-to-many и many-to-many, миграции Alembic, JWT-аутентификация, а также бизнес-логика обработки транзакций.
