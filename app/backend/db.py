from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

URL_DATABASE = "postgresql+asyncpg://postgres:postgres@localhost:5432/ernest_db"

engine = create_async_engine(URL_DATABASE)

async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
