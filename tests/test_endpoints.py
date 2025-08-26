from fastapi import APIRouter, HTTPException
from app.backend.cache import set_value, get_value, delete_key, key_exists
from app.backend.cache.celery_app import simple_task
import time

router = APIRouter(prefix="/test", tags=["Тестирование"])

# ========================================
# ТЕСТИРОВАНИЕ REDIS (КЕШИРОВАНИЕ)
# ========================================

@router.post("/redis/set")
async def test_redis_set():
    """Тест сохранения данных в Redis"""
    try:
        # Сохраняем тестовые данные
        set_value("test_user", "Тестовый пользователь", expire=300)  # 5 минут
        set_value("test_count", "42", expire=600)  # 10 минут
        
        return {
            "status": "success",
            "message": "Данные сохранены в Redis",
            "data": {
                "test_user": "Тестовый пользователь",
                "test_count": "42"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка Redis: {str(e)}")

@router.get("/redis/get")
async def test_redis_get():
    """Тест получения данных из Redis"""
    try:
        user = get_value("test_user")
        count = get_value("test_count")
        
        return {
            "status": "success",
            "data": {
                "test_user": user,
                "test_count": count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка Redis: {str(e)}")

@router.delete("/redis/clear")
async def test_redis_clear():
    """Тест очистки тестовых данных"""
    try:
        delete_key("test_user")
        delete_key("test_count")
        
        return {
            "status": "success",
            "message": "Тестовые данные удалены из Redis"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка Redis: {str(e)}")

# ========================================
# ТЕСТИРОВАНИЕ CELERY (ФОНОВЫЕ ЗАДАЧИ)
# ========================================

@router.post("/celery/simple")
async def test_celery_simple():
    """Тест простой фоновой задачи"""
    try:
        # Запускаем простую задачу
        result = simple_task.delay("Привет из FastAPI!")
        
        return {
            "status": "success",
            "message": "Простая задача запущена",
            "task_id": result.id,
            "task_status": result.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка Celery: {str(e)}")


@router.get("/celery/status/{task_id}")
async def test_celery_status(task_id: str):
    """Проверка статуса задачи"""
    try:
        # Импортируем Celery app для получения результата
        from app.backend.cache.celery_app import celery_app
        
        # Получаем результат задачи
        result = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "ready": result.ready()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса: {str(e)}")

# ========================================
# КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ
# ========================================

@router.post("/full-test")
async def test_full_functionality():
    """Комплексный тест всех функций"""
    try:
        results = {}
        
        # 1. Тест Redis
        set_value("full_test_key", "test_value", expire=60)
        redis_value = get_value("full_test_key")
        results["redis"] = {"status": "success", "value": redis_value}
        
        # 2. Тест Celery
        celery_result = simple_task.delay("Комплексный тест")
        results["celery"] = {"status": "success", "task_id": celery_result.id}
        
        
        # Очистка
        delete_key("full_test_key")
        
        return {
            "status": "success",
            "message": "Все функции протестированы",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка комплексного теста: {str(e)}")

# ========================================
# ИНФОРМАЦИЯ О СИСТЕМЕ
# ========================================

@router.get("/info")
async def get_system_info():
    """Получить информацию о системе"""
    return {
        "system": "FastAPI Ernesto Khachatyryan",
        "features": [
            "Redis кеширование",
            "Celery фоновые задачи", 
            "Email рассылка",
            "PostgreSQL база данных"
        ],
        "test_endpoints": [
            "POST /test/redis/set - Тест Redis (сохранение)",
            "GET /test/redis/get - Тест Redis (получение)",
            "DELETE /test/redis/clear - Тест Redis (очистка)",
            "POST /test/celery/simple - Тест Celery (простая задача)",
            "POST /test/celery/email - Тест Celery (email)",
            "GET /test/celery/status/{task_id} - Статус задачи",
            "POST /test/full-test - Комплексный тест",
            "GET /test/info - Эта информация"
        ]
    }