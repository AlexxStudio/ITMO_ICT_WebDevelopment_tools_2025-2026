from app.tasks import parse_url_task
from app.connection import init_db
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from app.connection import get_session
from app.models import (
    User, UserRead, UserRegister, UserLogin, ChangePassword,
    Account, AccountRead, Category, CategoryRead,
    Transaction, TransactionFull, Tag, TagRead,
    TransactionTag, Budget, FinanceSummary,
    ParsedPage
)
from app.auth import hash_password, verify_password, create_access_token
from app.auth import get_current_user
import requests

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }


@app.get("/")
def root():
    return {"message": "Finance API is running"}


# ---------------- AUTH / USER ----------------

@app.post("/register")
def register_user(user_data: UserRegister, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(
        User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this email already exists")

    hashed_password = hash_password(user_data.password)

    user = User(email=user_data.email, password=hashed_password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email}


@app.post("/login")
def login_user(user_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(
        User.email == user_data.email)).first()
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid email or password")

    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/users", response_model=list[UserRead])
def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}/change-password")
def change_password(
    user_id: int,
    password_data: ChangePassword,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="You can only change your own password")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password_data.old_password, user.password):
        raise HTTPException(
            status_code=400, detail="Old password is incorrect")

    user.password = hash_password(password_data.new_password)

    session.add(user)
    session.commit()

    return {"message": "Password changed successfully"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"message": "User deleted"}


# ---------------- ACCOUNT ----------------

@app.post("/accounts")
def create_account(account: Account, session: Session = Depends(get_session)):
    user = session.get(User, account.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@app.get("/accounts")
def get_accounts(session: Session = Depends(get_session)):
    accounts = session.exec(select(Account)).all()
    return accounts


@app.get("/accounts/{account_id}")
def get_account(account_id: int, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    session.delete(account)
    session.commit()
    return {"message": "Account deleted"}


# ---------------- CATEGORY ----------------

@app.post("/categories")
def create_category(category: Category, session: Session = Depends(get_session)):
    user = session.get(User, category.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@app.get("/categories")
def get_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category)).all()
    return categories


@app.get("/categories/{category_id}")
def get_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.delete("/categories/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"message": "Category deleted"}


# ---------------- TRANSACTION ----------------

@app.post("/transactions")
def create_transaction(transaction: Transaction, session: Session = Depends(get_session)):
    if transaction.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Transaction amount must be greater than 0")

    account = session.get(Account, transaction.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    category = session.get(Category, transaction.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.type == "income":
        account.balance += transaction.amount
    elif category.type == "expense":
        if account.balance - transaction.amount < 0:
            raise HTTPException(
                status_code=400, detail="Insufficient funds: balance cannot go below zero")
        account.balance -= transaction.amount
    else:
        raise HTTPException(
            status_code=400, detail="Category type must be 'income' or 'expense'")

    session.add(account)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    session.refresh(account)

    return {
        "message": "Transaction created successfully",
        "transaction": transaction,
        "updated_account_balance": account.balance
    }


@app.get("/transactions")
def get_transactions(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    return transactions


@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    account = session.get(Account, transaction.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    category = session.get(Category, transaction.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.type == "income":
        account.balance -= transaction.amount
    elif category.type == "expense":
        account.balance += transaction.amount

    session.add(account)
    session.delete(transaction)
    session.commit()
    session.refresh(account)

    return {
        "message": "Transaction deleted",
        "updated_account_balance": account.balance
    }


# ---------------- TAG ----------------

@app.post("/tags")
def create_tag(tag: Tag, session: Session = Depends(get_session)):
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@app.get("/tags")
def get_tags(session: Session = Depends(get_session)):
    tags = session.exec(select(Tag)).all()
    return tags


@app.get("/tags/{tag_id}")
def get_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    session.delete(tag)
    session.commit()
    return {"message": "Tag deleted"}


# ---------------- TRANSACTION TAG ----------------

@app.post("/transaction-tags")
def add_tag_to_transaction(transaction_tag: TransactionTag, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_tag.transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tag = session.get(Tag, transaction_tag.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    existing_link = session.get(
        TransactionTag,
        (transaction_tag.transaction_id, transaction_tag.tag_id)
    )
    if existing_link:
        raise HTTPException(
            status_code=400, detail="This tag is already linked to the transaction")

    session.add(transaction_tag)
    session.commit()
    session.refresh(transaction_tag)
    return transaction_tag


@app.get("/transaction-tags")
def get_transaction_tags(session: Session = Depends(get_session)):
    links = session.exec(select(TransactionTag)).all()
    return links


@app.delete("/transaction-tags")
def delete_tag_from_transaction(transaction_id: int, tag_id: int, session: Session = Depends(get_session)):
    link = session.get(TransactionTag, (transaction_id, tag_id))
    if not link:
        raise HTTPException(
            status_code=404, detail="TransactionTag link not found")

    session.delete(link)
    session.commit()
    return {"message": "Tag removed from transaction"}


# ---------------- BUDGET ----------------

@app.post("/budgets")
def create_budget(budget: Budget, session: Session = Depends(get_session)):
    user = session.get(User, budget.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    category = session.get(Category, budget.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@app.get("/my/budgets")
def get_my_budgets(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    budgets = session.exec(
        select(Budget).where(Budget.user_id == current_user.id)
    ).all()
    return budgets


@app.get("/budgets")
def get_budgets(session: Session = Depends(get_session)):
    budgets = session.exec(select(Budget)).all()
    return budgets


@app.get("/budgets/{budget_id}")
def get_budget(budget_id: int, session: Session = Depends(get_session)):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@app.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, session: Session = Depends(get_session)):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    session.delete(budget)
    session.commit()
    return {"message": "Budget deleted"}


@app.get("/transactions/{transaction_id}/full", response_model=TransactionFull)
def get_transaction_full(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    account = session.get(Account, transaction.account_id)
    category = session.get(Category, transaction.category_id)

    links = session.exec(
        select(TransactionTag).where(
            TransactionTag.transaction_id == transaction_id)
    ).all()

    tags = []
    for link in links:
        tag = session.get(Tag, link.tag_id)
        if tag:
            tags.append(tag)

    return {
        "id": transaction.id,
        "amount": transaction.amount,
        "description": transaction.description,
        "date": transaction.date,
        "account": account,
        "category": category,
        "tags": tags
    }


@app.get("/report/summary/{user_id}", response_model=FinanceSummary)
def get_finance_summary(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="You can view only your own report")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    accounts = session.exec(select(Account).where(
        Account.user_id == user_id)).all()

    total_income = 0.0
    total_expense = 0.0

    for account in accounts:
        transactions = session.exec(
            select(Transaction).where(Transaction.account_id == account.id)
        ).all()

        for transaction in transactions:
            category = session.get(Category, transaction.category_id)
            if not category:
                continue

            if category.type == "income":
                total_income += transaction.amount
            elif category.type == "expense":
                total_expense += transaction.amount

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }


@app.get("/my/report/summary", response_model=FinanceSummary)
def get_my_finance_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    accounts = session.exec(
        select(Account).where(Account.user_id == current_user.id)
    ).all()

    total_income = 0.0
    total_expense = 0.0

    for account in accounts:
        transactions = session.exec(
            select(Transaction).where(Transaction.account_id == account.id)
        ).all()

        for transaction in transactions:
            category = session.get(Category, transaction.category_id)
            if not category:
                continue

            if category.type == "income":
                total_income += transaction.amount
            elif category.type == "expense":
                total_expense += transaction.amount

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }


@app.post("/parse")
def parse_website(url: str, session: Session = Depends(get_session)):

    try:
        response = requests.post(
            "http://parser:8001/parse",
            json={"url": url},
            timeout=10
        )

        response.raise_for_status()

        parsed_data = response.json()

        parsed_page = ParsedPage(
            url=parsed_data["url"],
            title=parsed_data["title"]
        )

        session.add(parsed_page)
        session.commit()
        session.refresh(parsed_page)

        return {
            "message": "Page parsed successfully",
            "data": parsed_page
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-async")
def parse_website_async(url: str):
    task = parse_url_task.delay(url)

    return {
        "message": "Task added to queue",
        "task_id": task.id
    }


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = parse_url_task.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
