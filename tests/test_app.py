import requests
import time
import json

# Базовый URL вашего приложения
BASE_URL = "http://localhost:8000"

def test_redis():
    """Тестирование Redis функций"""
    print("🔴 Тестирование Redis...")
    
    # 1. Сохранение данных
    response = requests.post(f"{BASE_URL}/test/redis/set")
    if response.status_code == 200:
        print("✅ Данные сохранены в Redis")
    else:
        print(f"❌ Ошибка сохранения: {response.text}")
        return False
    
    # 2. Получение данных
    response = requests.get(f"{BASE_URL}/test/redis/get")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Данные получены из Redis: {data['data']}")
    else:
        print(f"❌ Ошибка получения: {response.text}")
        return False
    
    # 3. Очистка данных
    response = requests.delete(f"{BASE_URL}/test/redis/clear")
    if response.status_code == 200:
        print("✅ Данные очищены из Redis")
    else:
        print(f"❌ Ошибка очистки: {response.text}")
        return False
    
    return True

def test_celery():
    """Тестирование Celery функций"""
    print("\n🟢 Тестирование Celery...")
    
    # 1. Простая задача
    response = requests.post(f"{BASE_URL}/test/celery/simple")
    if response.status_code == 200:
        data = response.json()
        task_id = data['task_id']
        print(f"✅ Простая задача запущена, ID: {task_id}")
        
        # Ждем выполнения
        time.sleep(2)
        
        # Проверяем статус
        status_response = requests.get(f"{BASE_URL}/test/celery/status/{task_id}")
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ Статус задачи: {status_data['status']}")
            if status_data['ready']:
                print(f"✅ Результат: {status_data['result']}")
        else:
            print(f"❌ Ошибка проверки статуса: {status_response.text}")
    else:
        print(f"❌ Ошибка запуска задачи: {response.text}")
        return False
    
    return True


def test_full():
    """Комплексное тестирование"""
    print("\n🚀 Комплексное тестирование...")
    
    response = requests.post(f"{BASE_URL}/test/full-test")
    if response.status_code == 200:
        data = response.json()
        print("✅ Все функции протестированы успешно!")
        print(f"📊 Результаты: {json.dumps(data['results'], indent=2, ensure_ascii=False)}")
        return True
    else:
        print(f"❌ Ошибка комплексного теста: {response.text}")
        return False

def get_system_info():
    """Получение информации о системе"""
    print("\nℹ️  Информация о системе...")
    
    response = requests.get(f"{BASE_URL}/test/info")
    if response.status_code == 200:
        data = response.json()
        print(f"🏢 Система: {data['system']}")
        print("✨ Возможности:")
        for feature in data['features']:
            print(f"   • {feature}")
        return True
    else:
        print(f"❌ Ошибка получения информации: {response.text}")
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Начинаем тестирование FastAPI приложения...")
    print("=" * 50)
    
    # Проверяем доступность приложения
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Приложение доступно")
        else:
            print("❌ Приложение недоступно")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к приложению")
        print("💡 Убедитесь, что приложение запущено: uvicorn app.main:app --reload")
        return
    
    # Запускаем тесты
    tests = [
        ("Redis", test_redis),
        ("Celery", test_celery),
        ("Комплексный тест", test_full),
        ("Информация о системе", get_system_info)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
    
    # Выводим итоги
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("⚠️  Некоторые тесты не пройдены. Проверьте логи и настройки.")

if __name__ == "__main__":
    main()