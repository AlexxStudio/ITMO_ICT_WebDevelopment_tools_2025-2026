from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()


class Category(BaseModel):
    id: int
    name: str
    type: str  # income / expense


categories_db: List[Category] = []


@app.get("/")
def root():
    return {"message": "Finance API is running"}


# Получить все категории
@app.get("/categories")
def get_categories():
    return categories_db


# Получить категорию по id
@app.get("/categories/{category_id}")
def get_category(category_id: int):
    for category in categories_db:
        if category.id == category_id:
            return category
    raise HTTPException(status_code=404, detail="Category not found")


# Создать категорию
@app.post("/categories")
def create_category(category: Category):
    for existing_category in categories_db:
        if existing_category.id == category.id:
            raise HTTPException(status_code=400, detail="Category with this id already exists")

    categories_db.append(category)
    return category


# Обновить категорию
@app.put("/categories/{category_id}")
def update_category(category_id: int, updated_category: Category):
    for index, category in enumerate(categories_db):
        if category.id == category_id:
            categories_db[index] = updated_category
            return updated_category
    raise HTTPException(status_code=404, detail="Category not found")


# Удалить категорию
@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    for index, category in enumerate(categories_db):
        if category.id == category_id:
            deleted_category = categories_db.pop(index)
            return {"message": "Category deleted", "category": deleted_category}
    raise HTTPException(status_code=404, detail="Category not found")