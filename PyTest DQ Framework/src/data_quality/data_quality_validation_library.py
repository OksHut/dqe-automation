import pandas as pd
import numpy as np


class DataQualityLibrary:
    """
    Бібліотека для валідації даних між різними джерелами (Postgres, Parquet, etc.)
    """

    @staticmethod
    def check_dataset_is_not_empty(target_data: pd.DataFrame):
        """Перевіряє, чи набір даних не порожній."""
        print("DQ Check: Checking if dataset is not empty...")
        assert not target_data.empty, "Dataset is empty, but expected to have data."

    @staticmethod
    def check_count(source_data: pd.DataFrame, target_data: pd.DataFrame):
        """Порівнює кількість рядків у джерелі та цілі."""
        source_count = len(source_data)
        target_count = len(target_data)
        print(
            f"DQ Check: Row count comparison - Source: {source_count}, Target: {target_count}")

        assert source_count == target_count, \
            f"Row count mismatch! Source: {source_count}, Target: {target_count}"

    @staticmethod
    def check_data_completeness(source_data: pd.DataFrame, target_data: pd.DataFrame):
        """
        Перевіряє повну цілісність даних: чи всі записи з джерела присутні в таргеті.
        Використовує outer join для пошуку розбіжностей.
        """
        print("DQ Check: Checking data completeness (row-by-row comparison)...")

        # Сортуємо та скидаємо індекси для точного порівняння
        source = source_data.sort_values(
            by=list(source_data.columns)).reset_index(drop=True)
        target = target_data.sort_values(
            by=list(target_data.columns)).reset_index(drop=True)

        # Перевірка на ідентичність значень
        try:
            pd.testing.assert_frame_equal(
                source, target, check_dtype=False, check_like=True)
        except AssertionError as e:
            # Знаходимо конкретні рядки, яких не вистачає (diff)
            diff = pd.concat([source, target]).drop_duplicates(keep=False)
            print(f"Mismatch found in following rows:\n{diff.head(10)}")
            raise AssertionError(
                f"Data completeness check failed! Differences found in {len(diff)} rows.")

    @staticmethod
    def check_not_null_values(target_data: pd.DataFrame, columns: list):
        """Перевіряє вказані колонки на відсутність NULL значень."""
        print(f"DQ Check: Checking for NULL values in columns: {columns}")

        for col in columns:
            null_count = target_data[col].isnull().sum()
            assert null_count == 0, f"Column '{col}' contains {null_count} NULL values!"

    @staticmethod
    def check_duplicates(target_data: pd.DataFrame, subset: list = None):
        """Додаткова перевірка на унікальність рядків."""
        print(
            f"DQ Check: Checking for duplicates in subset: {subset if subset else 'all columns'}")
        duplicate_count = target_data.duplicated(subset=subset).sum()
        assert duplicate_count == 0, f"Found {duplicate_count} duplicate rows in target data!"

    @staticmethod
    def check_positive_values(target_data: pd.DataFrame, columns: list):
        """Перевірка, що числові значення (наприклад, ціни/суми) не є від'ємними."""
        for col in columns:
            min_val = target_data[col].min()
            assert min_val >= 0, f"Column '{col}' contains negative values (Min: {min_val})!"
