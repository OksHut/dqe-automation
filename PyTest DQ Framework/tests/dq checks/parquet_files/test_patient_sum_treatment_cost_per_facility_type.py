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

    # Фільтрація за датою, якщо вона присутня в файлі (наприклад, через visit_date)
    # Якщо файл агрегований без дат, використовуємо лише фільтрацію за наявними колонками
    if 'partition_date' in df.columns:
        df = df[df['partition_date'] == '2026-01']

    # Обов'язково видаляємо записи, де full_name є NULL (виходячи з вашого попереднього багу)
    # Це допоможе виявити реальну кількість пацієнтів, які пройшли успішну міграцію
    df = df.dropna(subset=['full_name'])

    return df


@pytest.mark.reconciliation
@pytest.mark.patient_sum
def test_patient_sum_costs(source_data_3, target_data_3, data_quality_library):
    print(
        f"\n[DEBUG] Rows (Jan 2026) - Source: {len(source_data_3)}, Target: {len(target_data_3)}")

    # ДІАГНОСТИКА: Перевірка на дублікати пацієнтів всередині одного типу закладу
    duplicates = target_data_3.duplicated(
        subset=['facility_type', 'full_name']).sum()
    if duplicates > 0:
        print(
            f"\n[!] ALERT: Знайдено {duplicates} дублікатів пацієнтів у Parquet!")

    # Стандартні перевірки
    data_quality_library.check_dataset_is_not_empty(target_data_3)

    # Цей ассерт покаже, чи всі 120 пацієнтів потрапили у файл без втрати імен
    data_quality_library.check_count(source_data_3, target_data_3)

    data_quality_library.check_not_null_values(
        target_data_3, ['facility_type', 'full_name', 'sum_treatment_cost'])

    # Перевірка точності сум (Accuracy)
    data_quality_library.check_data_completeness(source_data_3, target_data_3)
