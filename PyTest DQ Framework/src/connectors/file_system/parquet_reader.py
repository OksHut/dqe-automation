  
import os
import pandas as pd

class ParquetReader:
    @staticmethod
    def read_file(folder_name):
        # Отримуємо базовий шлях (/parquet_data)
        base_path = os.getenv('PARQUET_BASE_PATH', './src/data')
        
        # Формуємо повний шлях до папки з файлами
        full_path = os.path.join(base_path, folder_name)
        
        # Лог для відладки в Jenkins
        print(f"Reading dataset folder: {full_path}")
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Папку з даними не знайдено: {full_path}")
            
        # Якщо це папка, pandas (через двигун pyarrow) автоматично зчитає всі .parquet файли всередині
        return pd.read_parquet(full_path, engine='pyarrow')