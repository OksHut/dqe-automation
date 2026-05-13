import pytest
import pandas as pd


@pytest.fixture(scope='module')
def source_data_1(db_connection):
    """Отримуємо агреговані дані з Postgres."""
    query = """
    SELECT 
        f.facility_name, 
        v.visit_timestamp::date AS visit_date, 
        MIN(v.duration_minutes) AS min_time_spent
    FROM visits v
    JOIN facilities f ON f.id = v.facility_id
    WHERE v.visit_timestamp >= '2026-01-01' AND v.visit_timestamp < '2026-02-01'
    GROUP BY 1, 2
    ORDER BY 1, 2
    """
    return db_connection.get_data_sql(query)


@pytest.fixture(scope='module')
def target_data_1(parquet_reader, source_data_1):
    """Отримуємо дані з Parquet та фільтруємо по закладах із бази."""
    df = parquet_reader.read_file(
        'facility_name_min_time_spent_per_visit_date')

    if 'partition_date' in df.columns:
        df = df[df['partition_date'] == '2026-01']

    # КЛЮЧОВЕ ВИПРАВЛЕННЯ: Приведення типів
    df['visit_date'] = pd.to_datetime(df['visit_date']).dt.date
    valid_facilities = source_data_1['facility_name'].unique()

    df = df[df['facility_name'].isin(valid_facilities)]
    # Залишаємо вихідний датасет без жорсткого видалення рядків,
    # щоб тест міг завалідувати наявність NULL, якщо вони туди потраплять.
    return df


@pytest.mark.reconciliation
@pytest.mark.facility_min
def test_facility_min_time_spent(source_data_1, target_data_1, data_quality_library):
    # 1. Примусове приведення типів перед порівнянням (Double Check)
    source_data_1['visit_date'] = pd.to_datetime(
        source_data_1['visit_date']).dt.date
    target_data_1['visit_date'] = pd.to_datetime(
        target_data_1['visit_date']).dt.date

    print(
        f"\n[DEBUG] Rows - Source: {len(source_data_1)}, Target: {len(target_data_1)}")

    # 2. Глибока діагностика розбіжностей
    if len(source_data_1) != len(target_data_1):
        print("\n" + "="*50)
        print("АНАЛІЗ РОЗБІЖНОСТЕЙ (DIAGNOSTIC)")
        print("="*50)

        # Перевірка на дублікати в Parquet
        dupes = target_data_1.duplicated(
            subset=['facility_name', 'visit_date']).sum()
        if dupes > 0:
            print(
                f"[!] Знайдено {dupes} дублікатів комбінації [Facility + Date] у Parquet!")

        # Пошук конкретних пропущених дат або зайвих рядків
        merged = pd.merge(
            source_data_1[['facility_name', 'visit_date']],
            target_data_1[['facility_name', 'visit_date']],
            on=['facility_name', 'visit_date'],
            how='outer',
            indicator=True
        )

        mismatched = merged[merged['_merge'] != 'both']
        if not mismatched.empty:
            print("\nРізниця в наборах дат (перші 10):")
            print(mismatched.sort_values(['_merge', 'visit_date']).head(10))

            print("\nСтатистика розбіжностей по закладах:")
            print(mismatched.groupby(
                ['facility_name', '_merge'], observed=True).size())
        else:
            print(
                "\n[?] Набори дат ідентичні. Схоже, проблема в дубльованих рядках у Target.")
        print("="*50 + "\n")

    # 3. Основні перевірки фреймворку

    # КРОК 3.1: Перевірка на порожнечу
    data_quality_library.check_dataset_is_not_empty(target_data_1)

    # КРОК 3.2: НОВА ПЕРЕВІРКА NOT NULL (валідуємо ключі та бізнес-метрику)
    # Якщо в розрахунок мінімального часу потрапив NULL, тест відразу вкаже на це
    data_quality_library.check_not_null_values(
        target_data_1,
        columns=['facility_name', 'visit_date', 'min_time_spent']
    )

    # КРОК 3.3: Кількісна та покрокова звірка
    data_quality_library.check_count(source_data_1, target_data_1)
    data_quality_library.check_data_completeness(source_data_1, target_data_1)
