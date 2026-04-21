import pandas as pd
import os

class ParquetReader:
    @staticmethod
    def read_file(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Parquet file not found: {file_path}")
        return pd.read_parquet(file_path)