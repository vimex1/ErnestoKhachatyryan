from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete, update
from typing import Annotated
from slugify import slugify

from app.routers.auth import get_current_user
from app.backend.db_depends import get_db
from app.models import *
from app.schemas import CreateProduct

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_products(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    products = await db.scalars(select(Product).where(Product.is_active == True))
    all_products = products.all()

    if not all_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There a no product found"
        )

    return {"status_code": status.HTTP_200_OK, "response": all_products}


@router.post("/")
async def create_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    create_product: CreateProduct,
):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        category = await db.scalar(
            select(Category).where(
                Category.id == create_product.category_id, Category.is_active == True
            )
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {create_product.category_id} not found or inactive",
            )

        await db.execute(
            insert(Product).values(
                name=create_product.name,
                description=create_product.description,
                price=create_product.price,
                image_url=create_product.image_url,
                stock=create_product.stock,
                category_id=create_product.category_id,
                slug=slugify(create_product.name),
                rating=0.0,
                supplier_id=get_user.get('id')
            )
        )

        await db.commit()

        return {
            "status_code": status.HTTP_201_CREATED, 
            "transaction": "Successful"
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='You are not authorized for this metod'
            )


@router.get("/{product_slug}")
async def products_by_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_slug: str,
):

    category = await db.scalar(select(Category).where(Category.slug == category_slug))

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    async def get_subcategories(category_id: int) -> list[int]:
        """Рекурсивно возвращает список id вложенных подкатегорий"""
        result = [category_id]
        subcategories = await db.scalars(
            select(Category).where(Category.parent_id == category_id)
        )
        subcats = subcategories.all()

        for subcategory in subcats:
            sub_ids = await get_subcategories(subcategory.id)
            result.extend(sub_ids)
        return result

    category_ids = await get_subcategories(category.id)

    products = await db.scalars(
        select(Product).where(
            Product.category_id.in_(category_ids),
            Product.is_active == True,
            Product.stock > 0,
        )
    )
    products_by_category = products.all()

    async def category_tree(category_id: int) -> dict:
        """Рекурсивно строит дерево продуктов по категориям"""
        current_category = await db.scalar(
            select(Category).where(Category.id == category_id)
        )

        category_products = [
            product
            for product in products_by_category
            if product.category_id == category_id
        ]

        subcategories = await db.scalars(
            select(Category).where(Category.parent_id == category_id)
        )
        subcats = subcategories.all()

        subcategory_trees = []
        for subcat in subcats:
            subtree = await category_tree(subcat.id)
            subcategory_trees.append(subtree)

        return {
            "category_name": current_category.name,
            "products": category_products,
            "subcategories": subcategory_trees,
        }

    response = await category_tree(category.id)

    return {"status_code": status.HTTP_200_OK, "response": response}


@router.get("/detail/{product_slug}")
async def product_detail(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"status_code": status.HTTP_200_OK, "response": product}


@router.put("/{product_slug}")
async def update_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    product_slug: str,
    update_product: CreateProduct,
):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        product = await db.scalar(
            select(Product).where(Product.slug == product_slug, Product.is_active == True)
        )

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.name = update_product.name
        product.description = update_product.description
        product.price = update_product.price
        product.image_url = update_product.image_url
        product.stock = update_product.stock
        product.category_id = update_product.category_id
        product.slug = slugify(update_product.name)

        await db.commit()

        return {
            "status_code": status.HTTP_200_OK,
            "transaction": "Product update is successful",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='You are not authorized for this metod'
            )


@router.delete("/{product_slug}")
async def delete_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    product_slug: str,
):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        product = await db.scalar(select(Product).where(Product.slug == product_slug))

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.is_active = False

        await db.commit()

        return {
            "status_code": status.HTTP_200_OK,
            "transaction": "Product delete is successful",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='You are not authorized for this metod'
            )
