from pydantic import BaseModel
from typing import List


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str | None = "Missing image URL"
    stock: int
    category_id: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None
