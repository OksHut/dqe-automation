import os
import pytest
from dotenv import load_dotenv
from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.connectors.file_system.parquet_reader import ParquetReader
from src.data_quality.data_quality_validation_library import DataQualityLibrary

# 1. Завантажуємо змінні з .env файлу на самому початку
load_dotenv()

def pytest_addoption(parser):
    """
    Дозволяємо передавати параметри через термінал (наприклад, pytest --db_host=localhost).
    Якщо параметр не передано, Pytest не впаде, а використає None або default.
    """
    parser.addoption("--db_host", action="store", default=os.getenv("DB_HOST"))
    parser.addoption("--db_name", action="store", default=os.getenv("DB_NAME"))
    parser.addoption("--db_user", action="store", default=os.getenv("DB_USER"))
    parser.addoption("--db_pass", action="store", default=os.getenv("DB_PASS"))

@pytest.fixture(scope="session")
def db_connector(request):
    """
    Фікстура для створення конектора до БД. 
    Пріоритет: 
    1. Аргумент командного рядка (якщо вказано)
    2. Значення з .env (якщо аргумент не вказано)
    """
    # Отримуємо значення з опцій pytest (які вже мають дефолти з .env)
    host = request.config.getoption("--db_host")
    database = request.config.getoption("--db_name")
    user = request.config.getoption("--db_user")
    password = request.config.getoption("--db_pass")
    
    # ПЕРЕВІРКА: чи всі обов'язкові дані на місці
    if not all([database, user, password]):
        pytest.exit(f"Критична помилка: Відсутні дані для підключення до БД (DB_NAME, DB_USER або DB_PASS). "
                    f"Перевір файл .env або передай аргументи в терміналі.")

    return PostgresConnectorContextManager(
        host=host,
        database=database,
        user=user,
        password=password
    )

@pytest.fixture(scope='module')
def target_data(parquet_tool):
    """Отримуємо дані з папки паркетів"""
    # Назва папки, яка лежить всередині /parquet_data/
    folder_name = 'facility_name_min_time_spent_per_visit_date'
    return parquet_tool.read_file(folder_name)

@pytest.fixture(scope="session")
def dq_library():
    """Фікстура для доступу до бібліотеки валідацій"""
    return DataQualityLibrary()