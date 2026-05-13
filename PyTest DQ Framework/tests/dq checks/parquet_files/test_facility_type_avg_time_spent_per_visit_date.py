import pytest
import pandas as pd


@pytest.fixture(scope='module')
def source_data_2(db_connection):
    """Отримуємо агреговані дані з Postgres лише за січень 2026."""
    query = """
    SELECT 
        f.facility_type, 
        v.visit_timestamp::date AS visit_date, 
        ROUND(AVG(v.duration_minutes)::numeric, 2) AS avg_time_spent
    FROM visits v
    JOIN facilities f ON f.id = v.facility_id
    WHERE v.visit_timestamp >= '2026-01-01' AND v.visit_timestamp < '2026-02-01'
    GROUP BY 1, 2
    ORDER BY 1, 2
    """
    return db_connection.get_data_sql(query)


@pytest.fixture(scope='module')
def target_data_2(parquet_reader):
    """Отримуємо дані з Parquet, фільтруючи за партицією та датами січня."""
    df = parquet_reader.read_file(
        'facility_type_avg_time_spent_per_visit_date')

    # 1. Фільтрація за партицією
    if 'partition_date' in df.columns:
        df = df[df['partition_date'] == '2026-01']

    # 2. Приведення типів та фільтрація за діапазоном дат
    df['visit_date'] = pd.to_datetime(df['visit_date']).dt.date
    start_date = pd.to_datetime('2026-01-01').date()
    end_date = pd.to_datetime('2026-02-01').date()

    df = df[(df['visit_date'] >= start_date) & (df['visit_date'] < end_date)]

    return df.dropna(subset=['facility_type', 'visit_date'])


@pytest.mark.reconciliation
@pytest.mark.facility_avg
def test_facility_avg_time_spent(source_data_2, target_data_2, data_quality_library):
    # Синхронізація типів для Source (на випадок, якщо конектор повернув datetime)
    source_data_2['visit_date'] = pd.to_datetime(
        source_data_2['visit_date']).dt.date

    print(
        f"\n[DEBUG] Rows (Jan 2026) - Source: {len(source_data_2)}, Target: {len(target_data_2)}")

    # ДІАГНОСТИКА: Перевірка на дублікати перед основними ассертами
    duplicates = target_data_2.duplicated(
        subset=['facility_type', 'visit_date']).sum()
    if duplicates > 0:
        print(
            f"\n[!] ALERT: Знайдено {duplicates} дублікатів у Parquet для січня!")
        # Опційно: видаляємо дублікати для продовження тестування значень
        # target_data_2 = target_data_2.drop_duplicates(subset=['facility_type', 'visit_date'])

    # Стандартні перевірки бібліотеки
    data_quality_library.check_dataset_is_not_empty(target_data_2)
    data_quality_library.check_count(source_data_2, target_data_2)
    data_quality_library.check_not_null_values(
        target_data_2, ['facility_type', 'visit_date', 'avg_time_spent'])

    # Порівняння значень (Completeness & Accuracy)
    data_quality_library.check_data_completeness(source_data_2, target_data_2)
