"""
Description: Data Quality reconciliation checks for Visits
Requirement(s): TICKET-1234
Author(s): Oksana Hutnyk
"""
import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    """Отримуємо дані з Postgres. db_connection вже відкритий у conftest."""
    source_query = "SELECT * FROM visits"
    # Просто викликаємо метод, з'єднання вже керується фікстурою
    return db_connection.get_data_sql(source_query)


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    """Отримуємо дані з Parquet папки за допомогою parquet_reader."""
    folder_name = 'facility_name_min_time_spent_per_visit_date'
    return parquet_reader.read_file(folder_name)


@pytest.mark.parquet_data
@pytest.mark.example
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    """Перевірка, що завантажений файл не порожній"""
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.example
@pytest.mark.reconciliation
def test_check_count(source_data, target_data, data_quality_library):
    """Звірка кількості записів між БД та файлом"""
    data_quality_library.check_count(source_data, target_data)
