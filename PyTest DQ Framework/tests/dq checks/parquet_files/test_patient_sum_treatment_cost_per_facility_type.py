import pytest
import pandas as pd


@pytest.fixture(scope='module')
def source_data_3(db_connection):
    """
    Отримуємо сумарні витрати пацієнтів за січень 2026.
    Логіка: full_name = first_name + space + last_name
    """
    query = """
    SELECT 
        f.facility_type, 
        p.first_name || ' ' || p.last_name AS full_name,
        SUM(v.treatment_cost) AS sum_treatment_cost
    FROM visits v
    JOIN facilities f ON f.id = v.facility_id
    JOIN patients p ON p.id = v.patient_id
    WHERE v.visit_timestamp >= '2026-01-01' AND v.visit_timestamp < '2026-02-01'
    GROUP BY 1, 2
    ORDER BY 1, 2
    """
    return db_connection.get_data_sql(query)


@pytest.fixture(scope='module')
def target_data_3(parquet_reader):
    """Отримуємо дані з Parquet, фільтруючи за партицією типу закладу та січнем."""
    df = parquet_reader.read_file(
        'patient_sum_treatment_cost_per_facility_type')

    if 'partition_date' in df.columns:
        df = df[df['partition_date'] == '2026-01']

    # ВАЖЛИВО: Ми більше не видаляємо NULL локально через .dropna().
    # Ми хочемо, щоб бібліотека DQ виявила їх і видала помилку у звіті.
    return df


@pytest.mark.reconciliation
@pytest.mark.patient_sum
def test_patient_sum_costs(source_data_3, target_data_3, data_quality_library):
    print(
        f"\n[DEBUG] Rows (Jan 2026) - Source: {len(source_data_3)}, Target: {len(target_data_3)}")

    # ДІАГНОСТИКА: Перевірка на дублікати
    duplicates = target_data_3.duplicated(
        subset=['facility_type', 'full_name']).sum()
    if duplicates > 0:
        print(
            f"\n[!] ALERT: Знайдено {duplicates} дублікатів пацієнтів у Parquet!")

    # --- СТАНДАРТНІ ПЕРЕВІРКИ БІБЛІОТЕКИ ---

    # 1. Перевірка на наявність даних
    data_quality_library.check_dataset_is_not_empty(target_data_3)

    # 2. Перевірка на NULL (Критично для full_name та вартості лікування)
    # Тепер, якщо в даних будуть порожні імена, тест впаде саме тут.
    data_quality_library.check_not_null_values(
        target_data_3,
        ['facility_type', 'full_name', 'sum_treatment_cost']
    )

    # 3. Кількісна звірка (Row Count Completeness)
    data_quality_library.check_count(source_data_3, target_data_3)

    # 4. Перевірка точності сум та повноти записів (Accuracy)
    data_quality_library.check_data_completeness(source_data_3, target_data_3)
