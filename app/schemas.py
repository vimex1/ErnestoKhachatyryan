from pydantic import BaseModel, Field
from datetime import datetime


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str = "Missing image URL"
    stock: int
    category_id: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class CreateReview(BaseModel):
    comment: str = 'Введите ваш отзыв...'
    grade: int = 5