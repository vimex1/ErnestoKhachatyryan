from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from typing import Annotated
from datetime import datetime

from app.routers.auth import get_current_user
from app.backend.db_depends import get_db
from app.models import *
from app.schemas import CreateReview

router = APIRouter(prefix="/reviews", tags=["reviews"])


async def update_rating() -> None:
    pass

@router.get("/")
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Получить все активные отзывы.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        dict: Статус и список всех активных отзывов
        
    Raises:
        HTTPException: Если отзывы не найдены
    """
    reviews = await db.scalars(select(Review).where(Product.is_active == True))
    all_reviews = reviews.all()

    if not all_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There a no reviews found"
        )

    return {"status_code": status.HTTP_200_OK, "response": all_reviews}


@router.get("/{product_slug}")
async def products_reviews(
    db: Annotated[AsyncSession, Depends(get_db)], product_id: int
):
    """
    Получить все отзывы для конкретного продукта.
    
    Args:
        db: Сессия базы данных
        product_id: ID продукта
        
    Returns:
        dict: Статус и список отзывов для продукта
        
    Raises:
        HTTPException: Если отзывы для продукта не найдены
    """
    products_reviews = await db.scalars(
        select(Review).where(Review.product_id == product_id, Review.is_active == True)
    )
    prod_all_reviews = products_reviews.all()

    if not prod_all_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviews for this product not founded",
        )

    return {"status_code": status.HTTP_200_OK, "response": prod_all_reviews}


@router.post("/")
async def add_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    product_id: int,
    create_review: CreateReview,
):
    """
    Добавить новый отзыв к продукту.
    
    Требует права покупателя. Автоматически обновляет рейтинг продукта.
    
    Args:
        db: Сессия базы данных
        get_user: Текущий аутентифицированный пользователь
        product_id: ID продукта для отзыва
        create_review: Данные отзыва
        
    Returns:
        dict: Статус операции создания отзыва
        
    Raises:
        HTTPException: Если продукт не найден, оценка некорректна или у пользователя нет прав покупателя
    """
    if get_user.get("is_customer"):
        product = await db.scalar(
            select(Product).where(Product.id == product_id, Product.is_active == True)
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No product with {product_id=} found to leave a review",
            )

        if not 1 <= create_review.grade <= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Grade must be between 1 and 5",
            )

        await db.execute(
            insert(Review).values(
                user_id=get_user.get("id"),
                comment=create_review.comment,
                comment_date=datetime.now(),
                grade=create_review.grade,
                product_id=product_id,
            )
        )

        grades = await db.scalars(
            select(Review).where(
                Review.product_id == product_id, Review.is_active == True
            )
        )
        all_grades = [grade.grade for grade in grades.all()]

        product.rating = round(sum(all_grades) / len(all_grades), 2)

        db.add(product)
        await db.commit()

        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admins and suppliers can't leave the review. You must be a customer for this.",
        )


@router.delete("/{review_id}")
async def delete_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    review_id: int,
):
    """
    Удалить отзыв (деактивировать).
    
    Требует права администратора. Отзыв помечается как неактивный.
    Автоматически пересчитывает рейтинг продукта.
    
    Args:
        db: Сессия базы данных
        get_user: Текущий аутентифицированный пользователь
        review_id: ID отзыва для удаления
        
    Returns:
        dict: Статус операции удаления отзыва
        
    Raises:
        HTTPException: Если у пользователя нет прав администратора
    """
    if get_user.get("is_admin"):
        review = await db.scalar(
            select(Review).where(Review.id == review_id, Review.is_active == True)
        )

        review.is_active = False

        # Вывести в отдельную функцию
        #-------------vvv-------------
        product = await db.scalar(
            select(Product).where(Product.id == review.product_id, Product.is_active == True)
        )

        grades = await db.scalars(
            select(Review).where(
                Review.product_id == review.product_id, Review.is_active == True
            )
        )
        all_grades = [grade.grade for grade in grades.all()]

        product.rating = round(sum(all_grades) / len(all_grades), 2)
        #-------------^^^-------------

        db.add(product)
        await db.commit()

        return {
            "status_code": status.HTTP_200_OK,
            "transaction": "Review delete is successful",
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are must be admin for this metod",
        )
