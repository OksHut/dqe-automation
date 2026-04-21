import pandas as pd

class DataQualityLibrary:
    """
    Професійна бібліотека для валідації якості даних.
    Кожен метод виконує перевірку та викидає AssertionError з описом помилки.
    """

    @staticmethod
    def check_duplicates(df, column_names=None):
        """Перевіряє наявність дублікатів у вказаних колонках або в усьому датасеті."""
        subset = column_names if column_names else df.columns.tolist()
        duplicate_count = df.duplicated(subset=subset).sum()
        
        assert duplicate_count == 0, f"DQ Failure: Found {duplicate_count} duplicate rows in columns: {subset}"

    @staticmethod
    def check_count(df_source, df_target):
        """Порівнює кількість рядків у двох датасетах (наприклад, Source vs Target)."""
        count_source = len(df_source)
        count_target = len(df_target)
        
        assert count_source == count_target, \
            f"DQ Failure: Row count mismatch! Source: {count_source}, Target: {count_target}"

    @staticmethod
    def check_dataset_is_not_empty(df):
        """Перевіряє, що датасет містить дані."""
        assert not df.empty, "DQ Failure: The dataset is empty!"

    @staticmethod
    def check_not_null_values(df, column_names=None):
        """Перевіряє відсутність NULL значень у вказаних колонках."""
        cols_to_check = column_names if column_names else df.columns.tolist()
        
        for col in cols_to_check:
            null_count = df[col].isnull().sum()
            assert null_count == 0, f"DQ Failure: Column '{col}' has {null_count} null values."

    @staticmethod
    def check_full_data_set_equality(df1, df2):
        """Повне порівняння двох датасетів (значення в значення)."""
        # Спершу перевіримо розмірність для швидкості
        assert df1.shape == df2.shape, f"DQ Failure: Shape mismatch {df1.shape} vs {df2.shape}"
        
        # Порівнюємо вміст (повертає boolean маску)
        pd.testing.assert_frame_equal(df1, df2)