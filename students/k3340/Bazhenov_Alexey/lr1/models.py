from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class TransactionTag(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None,
        foreign_key="transaction.id",
        primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True
    )
    note: Optional[str] = None


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password: str

    accounts: List["Account"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    balance: float = 0.0
    user_id: int = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="accounts")
    transactions: List["Transaction"] = Relationship(back_populates="account")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str
    user_id: int = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    description: Optional[str] = None
    date: str
    account_id: int = Field(foreign_key="account.id")
    category_id: int = Field(foreign_key="category.id")

    account: Optional[Account] = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")
    tags: List["Tag"] = Relationship(
        back_populates="transactions",
        link_model=TransactionTag
    )


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    transactions: List[Transaction] = Relationship(
        back_populates="tags",
        link_model=TransactionTag
    )


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    limit_amount: float
    period: str
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    user: Optional[User] = Relationship(back_populates="budgets")
    category: Optional[Category] = Relationship(back_populates="budgets")


class UserRegister(SQLModel):
    email: str
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class ChangePassword(SQLModel):
    old_password: str
    new_password: str


class UserRead(SQLModel):
    id: int
    email: str


class AccountRead(SQLModel):
    id: int
    name: str
    balance: float
    user_id: int


class CategoryRead(SQLModel):
    id: int
    name: str
    type: str
    user_id: int


class TagRead(SQLModel):
    id: int
    name: str


class TransactionFull(SQLModel):
    id: int
    amount: float
    description: Optional[str] = None
    date: str
    account: AccountRead
    category: CategoryRead
    tags: List[TagRead]


class FinanceSummary(SQLModel):
    total_income: float
    total_expense: float
    balance: float