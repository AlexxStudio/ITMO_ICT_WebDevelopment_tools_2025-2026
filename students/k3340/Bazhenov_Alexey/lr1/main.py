from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from connection import init_db, get_session
from models import Category

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Finance API with database is running"}


@app.post("/categories")
def create_category(category: Category, session: Session = Depends(get_session)):
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


# Обновить категорию
@app.put("/categories/{category_id}")
def update_category(category_id: int, updated_category: Category, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = updated_category.name
    category.type = updated_category.type

    session.add(category)
    session.commit()
    session.refresh(category)

    return category


# Удалить категорию
@app.delete("/categories/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()

    return {"message": "Category deleted"}