"""
Description: Data Quality checks ...
Requirement(s): TICKET-1234
Author(s): Name Surname
"""

import pytest

@pytest.mark.db_check
@pytest.mark.dq_check
def test_facility_min_duration_validation(db_connector, dq_library):
    
    
    # --- ARRANGE (Підготовка) ---
    # Бізнес-поріг згідно з вимогами
    MIN_DURATION_LIMIT = 5
    
   
    query = """
        SELECT 
            f.facility_name, 
            v.visit_timestamp, 
            v.duration_minutes
        FROM visits v
        JOIN facilities f ON v.facility_id = f.id
    """

    # --- ACT
    # PostgresConnector (через Context Manager)
    with db_connector as db:
        df = db.get_data_sql(query)

    # --- ASSERT (Перевірка) ---
    
    # 1. Перевірка, що запит повернув дані
    dq_library.check_dataset_is_not_empty(df)

    # 2. Перевірка на відсутність пустих значень (NULL) у колонках результату
    dq_library.check_not_null_values(df, column_names=['duration_minutes', 'facility_name'])

    # 3. Основна перевірка: чи є візити, коротші за встановлений ліміт
    # Фільтруємо датафрейм, щоб знайти порушення
    invalid_records = df[df['duration_minutes'] < MIN_DURATION_LIMIT]
    
    # Якщо список порушень не порожній — тест впаде з детальним описом
    assert invalid_records.empty, \
        f"DQ Failure: Знайдено {len(invalid_records)} візитів коротших за {MIN_DURATION_LIMIT} хв. " \
        f"Приклади порушень: \n{invalid_records[['facility_name', 'duration_minutes']].head()}"

    # 4. Додаткова перевірка: перевіряємо, чи немає від'ємних значень (технічний баг)
    assert df['duration_minutes'].min() >= 0, "Критична помилка: Виявлено візити з від'ємною тривалістю!"
