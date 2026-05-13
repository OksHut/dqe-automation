import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class ParquetReader:
    @staticmethod
    def read_file(folder_name: str) -> pd.DataFrame:
        """
        Зчитує набір parquet-файлів з папки.
        Підтримує автоматичне розпізнавання партицій.
        """
        base_path = os.getenv('PARQUET_BASE_PATH', './src/data')
        full_path = os.path.join(base_path, folder_name)

        logger.info(f"Reading dataset folder: {full_path}")

        if not os.path.exists(full_path):
            error_msg = f"Parquet folder not found: {full_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            # Використовуємо engine='pyarrow' для високої швидкості
            # Параметр engine='pyarrow' за замовчуванням підтримує partitioned datasets
            df = pd.read_parquet(full_path, engine='pyarrow')

            if df.empty:
                logger.warning(f"Dataset at {full_path} is empty.")

            return df

        except Exception as e:
            logger.error(
                f"Failed to read parquet data at {full_path}: {str(e)}")
            raise ValueError(f"Помилка при зчитуванні Parquet: {e}")

    @staticmethod
    def list_available_datasets():
        """Корисний метод для відладки: виводить список доступних папок з даними"""
        base_path = os.getenv('PARQUET_BASE_PATH', './src/data')
        if os.path.exists(base_path):
            return os.listdir(base_path)
        return []
