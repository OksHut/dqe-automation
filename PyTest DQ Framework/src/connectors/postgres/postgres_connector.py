import psycopg2
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class PostgresConnectorContextManager:
    def __init__(self, host, database, user, password, port=5432):
        self.db_config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port
        }
        self.connection = None

    def __enter__(self):
        """Відкриття з'єднання при вході в блок with"""
        try:
            logger.info(f"Connecting to PostgreSQL database: {self.db_config['database']}")
            self.connection = psycopg2.connect(**self.db_config)
            return self
        except Exception as e:
            logger.error(f"Failed to connect to DB: {e}")
            raise

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Автоматичне закриття з'єднання при виході з блоку with"""
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL connection closed.")
        
        if exc_type:
            logger.error(f"An error occurred during DB operation: {exc_value}")
            # Повертаємо False, щоб виключення прокидалося далі, якщо це потрібно для тесту
            return False

    def get_data_sql(self, sql: str) -> pd.DataFrame:
        """Виконання SQL запиту та повернення результату як Pandas DataFrame"""
        if not self.connection:
            raise ConnectionError("Database connection is not established. Use 'with' statement.")
        
        try:
            logger.info(f"Executing SQL query: {sql[:50]}...") # Логуємо початок запиту
            df = pd.read_sql_query(sql, self.connection)
            return df
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise