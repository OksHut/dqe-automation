import psycopg2
import pandas as pd
import logging
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


class PostgresConnectorContextManager:
    def __init__(self, host, database, user, password, port=5434):
        self.db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.db_config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port
        }
        self.connection = None
        self.engine = None

    def __enter__(self):
        try:
            logger.info(f"Connecting to DB: {self.db_config['database']}")
            # Використовуємо psycopg2 для базового з'єднання
            self.connection = psycopg2.connect(**self.db_config)
            # Встановлюємо Read Only сесію для безпеки DQ тестів
            self.connection.set_session(readonly=True, autocommit=True)
            return self
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL connection closed.")
        return False  # Дозволяємо виключенням прокидатися в Pytest

    def get_data_sql(self, sql: str) -> pd.DataFrame:
        if not self.connection:
            raise ConnectionError(
                "Connection not established. Use 'with' statement.")

        try:
            logger.info(
                f"Executing SQL: {sql.strip().replace(chr(10), ' ')[:70]}...")
            # Важливо: Pandas краще працює з SQLAlchemy, але може працювати і так
            df = pd.read_sql_query(sql, self.connection)
            return df
        except Exception as e:
            logger.error(f"Error during SQL execution: {e}")
            raise
