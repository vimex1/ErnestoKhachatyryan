from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Annotated
import jwt

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db
from app.backend.config import SECRET_KEY, ALGORITHM


router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def create_access_token(
    username: str,
    user_id: int,
    is_admin: bool,
    is_supplier: bool,
    is_customer: bool,
    expires_delta: timedelta,
):
    """
    Создать JWT токен доступа для пользователя.
    
    Args:
        username: Имя пользователя
        user_id: ID пользователя
        is_admin: Права администратора
        is_supplier: Права поставщика
        is_customer: Права покупателя
        expires_delta: Время жизни токена
        
    Returns:
        str: Закодированный JWT токен
    """
    payload = {
        "sub": username,
        "id": user_id,
        "is_admin": is_admin,
        "is_supplier": is_supplier,
        "is_customer": is_customer,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }

    # Преобразование datetime в timestamp
    payload["exp"] = int(payload["exp"].timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Получить текущего пользователя из JWT токена.
    
    Args:
        token: JWT токен из заголовка Authorization
        
    Returns:
        dict: Информация о пользователе
        
    Raises:
        HTTPException: Если токен недействителен или истек
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get('sub')
        user_id: int | None = payload.get('id')
        is_admin: bool | None = payload.get('is_admin')
        is_supplier: bool | None = payload.get('is_supplier')
        is_customer: bool | None = payload.get('is_customer')
        expire: int | None = payload.get('exp')

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )

        return {
            'username': username,
            'id': user_id,
            'is_admin': is_admin,
            'is_supplier': is_supplier,
            'is_customer': is_customer,
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired!"
        )
    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )


async def authenticate_user(
    db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str
):
    """
    Аутентифицировать пользователя по имени и паролю.
    
    Args:
        db: Сессия базы данных
        username: Имя пользователя
        password: Пароль пользователя
        
    Returns:
        User: Объект пользователя если аутентификация успешна
        
    Raises:
        HTTPException: Если учетные данные неверны или пользователь неактивен
    """
    user = await db.scalar(select(User).where(User.username == username))

    if (
        not user
        or not bcrypt_context.verify(password, user.hashed_password)
        or user.is_active == False
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser
):
    """
    Создать нового пользователя.
    
    Args:
        db: Сессия базы данных
        create_user: Данные для создания пользователя
        
    Returns:
        dict: Статус операции создания пользователя
    """
    await db.execute(
        insert(User).values(
            first_name=create_user.first_name,
            last_name=create_user.last_name,
            username=create_user.username,
            email=create_user.email,
            hashed_password=bcrypt_context.hash(create_user.password),
        )
    )
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.post("/token")
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Аутентификация пользователя и получение JWT токена.
    
    Args:
        db: Сессия базы данных
        form_data: Форма с учетными данными пользователя
        
    Returns:
        dict: JWT токен доступа и его тип
        
    Raises:
        HTTPException: Если учетные данные неверны
    """
    user = await authenticate_user(db, form_data.username, form_data.password)

    token = await create_access_token(
        user.username,
        user.id,
        user.is_admin,
        user.is_supplier,
        user.is_customer,
        expires_delta=timedelta(minutes=20),
    )
    return {"access_token": token, "token_type": "bearer"}

    

@router.get('/read_current_user')
async def read_current_user(user: dict = Depends(get_current_user)):
    """
    Получить информацию о текущем аутентифицированном пользователе.
    
    Args:
        user: Текущий пользователь из токена
        
    Returns:
        dict: Информация о текущем пользователе
    """
    return {'User': user}