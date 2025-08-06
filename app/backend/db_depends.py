from app.backend.db import SessionLocal


async def get_db():
    """Получение подключения к базе данных"""
    db = SessionLocal()
    try:
        yield db  
    finally:
        db.close()
        
