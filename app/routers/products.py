from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, delete, update
from slugify import slugify

from app.backend.db_depends import get_db
from app.models.products import Product
from app.models.category import Category
from app.schemas import CategoryProductsResponse, CreateProduct, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True)).all()
    return products


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product(
    db: Annotated[Session, Depends(get_db)], create_product: CreateProduct
):
    category = db.scalar(
        select(Category).where(
            Category.id == create_product.category_id,
            Category.is_active == True
        )
    )
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {create_product.category_id} not found or inactive"
        )

    db.execute(
        insert(Product).values(
            name=create_product.name,
            description=create_product.description,
            price=create_product.price,
            image_url=create_product.image_url,
            stock=create_product.stock,
            category_id=create_product.category_id,
            slug=slugify(create_product.name),
            rating=0.0,
        )
    )
    db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.get("/{product_slug}")
async def products_by_category(
    db: Annotated[Session, Depends(get_db)], category_slug: str
):

    category = db.scalar(select(Category).where(Category.slug == category_slug))

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    def get_subcategories(category_id: int) -> list[int]:
        """Рекурсивно возвращает список id вложенных подкатегорий"""
        result = [category_id]
        subcategories = db.scalars(
            select(Category).where(Category.parent_id == category_id)
        ).all()

        for subcategory in subcategories:
            result.extend(get_subcategories(subcategory.id))
        return result

    category_ids = get_subcategories(category.id)

    products_by_category = db.scalars(
        select(Product).where(
            Product.category_id.in_(category_ids),
            Product.is_active == True,
            Product.stock > 0,
        )
    ).all()

    def category_tree(category_id: int) -> dict:
        """Рекурсивно строит дерево продуктов по категориям"""
        current_category = db.scalar(select(Category).where(Category.id == category_id))

        category_products = [
            product
            for product in products_by_category
            if product.category_id == category_id
        ]

        subcategories = db.scalars(
            select(Category).where(Category.parent_id == category_id)
        ).all()

        return {
            "category_name": current_category.name,
            "products": category_products,
            "subcategories": [category_tree(subcat.id) for subcat in subcategories]
        }

    return category_tree(category.id)


@router.get("/detail/{product_slug}")
async def product_detail(
    db: Annotated[Session, Depends(get_db)], product_slug: str
):
    product = db.scalar(select(Product).where(Product.slug == product_slug))

    if not product:
        raise HTTPException(
            status_code=404, detail="Product not found"
        )
    
    return product


@router.put("/{product_slug}")
async def update_product(
    db: Annotated[Session, Depends(get_db)], 
    product_slug: str, 
    update_category: CreateProduct
):
    product = db.scalar(select(Product).where(Product.slug == product_slug))

    if not product:
        raise HTTPException(
            status_code=404, detail="Product not found"
        )
    
    db.execute(
        update(Product)
        .where(Product.slug == product_slug)
        .values(
            name=update_category.name,
            description=update_category.description,
            price=update_category.price,
            image_url=update_category.image_url,
            stock=update_category.stock,
            category_id=update_category.category_id
        )
    )

    db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Product update is successful",
        }


@router.delete("/{product_slug}")
async def delete_product(
    db: Annotated[Session, Depends(get_db)], 
    product_slug: str,
    ):
    
    product = db.scalar(select(Product).where(Product.slug == product_slug))

    if not product:
        raise HTTPException(
            status_code=404, detail="Product not found"
        )
    
    db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
    db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Product delete is successful",
        } 
