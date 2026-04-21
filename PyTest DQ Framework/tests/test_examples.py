"""
Description: Data Quality checks ...
Requirement(s): TICKET-1234
Author(s): Name Surname
"""
import pytest

@pytest.fixture(scope='module')
def source_data(db_connector):
    """Отримуємо дані з Postgres"""
    source_query = "SELECT * FROM visits" 
    # Використовуємо db_connector як context manager
    with db_connector as db:
        return db.get_data_sql(source_query)

@pytest.fixture(scope='module')
def target_data(parquet_tool):
    """Отримуємо дані з Parquet файлу"""
    
    target_path = 'src/data/facility_visits.parquet'
    return parquet_tool.read_file(target_path)

@pytest.mark.example
def test_check_dataset_is_not_empty(target_data, dq_library):
    """Перевірка, що завантажений файл не порожній"""
    dq_library.check_dataset_is_not_empty(target_data)

@pytest.mark.example
def test_check_count(source_data, target_data, dq_library):
    """Звірка кількості записів між БД та файлом"""
    dq_library.check_count(source_data, target_data)

