import os
import pytest
from dotenv import load_dotenv
from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.connectors.file_system.parquet_reader import ParquetReader
from src.data_quality.data_quality_validation_library import DataQualityLibrary

# Завантажуємо змінні оточення
load_dotenv()


def pytest_addoption(parser):
    """Додаємо параметри командного рядка."""
    parser.addoption("--db_host", action="store",
                     default=os.getenv("DB_HOST", "localhost"))
    parser.addoption("--db_name", action="store",
                     default=os.getenv("DB_NAME", "mydatabase"))
    parser.addoption("--db_port", action="store",
                     default=os.getenv("DB_PORT", "5432"))
    parser.addoption("--db_user", action="store", default=os.getenv("DB_USER"))
    parser.addoption("--db_password", action="store",
                     default=os.getenv("DB_PASS"))


def pytest_configure(config):
    """Валідація обов'язкових параметрів перед стартом."""
    required_options = ["--db_user", "--db_password"]
    for option in required_options:
        if not config.getoption(option):
            pytest.exit(
                f"Missing required option: {option}. Check your .env file or CLI arguments.")


@pytest.fixture(scope='session')
def db_connection(request):
    """Фікстура для підключення до БД (еталонна реалізація)."""
    db_params = {
        "host": request.config.getoption("--db_host"),
        "database": request.config.getoption("--db_name"),
        "port": request.config.getoption("--db_port"),
        "user": request.config.getoption("--db_user"),
        "password": request.config.getoption("--db_password")
    }

    try:
        with PostgresConnectorContextManager(**db_params) as db_connector:
            yield db_connector
    except Exception as e:
        pytest.fail(f"Failed to initialize PostgresConnector: {e}")


@pytest.fixture(scope='session')
def parquet_reader():
    """Фікстура для зчитування Parquet."""
    try:
        return ParquetReader()
    except Exception as e:
        pytest.fail(f"Failed to initialize ParquetReader: {e}")


@pytest.fixture(scope='session')
def data_quality_library():
    """Фікстура для DQ бібліотеки."""
    return DataQualityLibrary()
