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
    """
    parser.addoption("--db_host", action="store", default=os.getenv("DB_HOST"))
    parser.addoption("--db_name", action="store", default=os.getenv("DB_NAME"))
    parser.addoption("--db_user", action="store", default=os.getenv("DB_USER"))
    parser.addoption("--db_pass", action="store", default=os.getenv("DB_PASS"))

@pytest.fixture(scope="session")
def db_connector(request):
    """
    Фікстура для створення конектора до БД. 
    """
    host = request.config.getoption("--db_host")
    database = request.config.getoption("--db_name")
    user = request.config.getoption("--db_user")
    password = request.config.getoption("--db_pass")
    
    if not all([database, user, password]):
        pytest.exit(f"Критична помилка: Відсутні дані для підключення до БД. "
                    f"Перевір файл .env або передай аргументи в терміналі.")

    return PostgresConnectorContextManager(
        host=host,
        database=database,
        user=user,
        password=password
    )

@pytest.fixture(scope="session")
def parquet_tool():
    """
    НОВА ФІКСТУРА: Створює екземпляр конектора для роботи з Parquet.
    Саме її не міг знайти Pytest у попередньому запуску.
    """
    return ParquetReader()

@pytest.fixture(scope='module')
def target_data(parquet_tool):
    """
    Фікстура для завантаження даних з Parquet папки.
    """
    folder_name = 'facility_name_min_time_spent_per_visit_date'
    return parquet_tool.read_file(folder_name)

@pytest.fixture(scope="session")
def dq_library():
    """Фікстура для доступу до бібліотеки валідацій"""
    return DataQualityLibrary()