import pymysql
from contextlib import contextmanager
from urllib.parse import urlparse
from src.core.config import settings

class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        parsed = urlparse(database_url)
        self.scheme = parsed.scheme
        self.parsed = parsed
        self.database_name = parsed.path.lstrip("/")

        if not self.database_name:
            raise RuntimeError("DATABASE_URL debe incluir el nombre de la base de datos.")

    @property
    def is_mysql(self) -> bool:
        return self.scheme.startswith("mysql")

    def _connection_kwargs(self, include_database: bool = True) -> dict:
        kwargs = {
            "host": self.parsed.hostname or "localhost",
            "port": self.parsed.port or 3306,
            "user": self.parsed.username,
            "password": self.parsed.password,
            "cursorclass": pymysql.cursors.DictCursor,
            "autocommit": False,
        }
        if include_database:
            kwargs["database"] = self.database_name
        return kwargs

    @contextmanager
    def connect(self):
        if not self.is_mysql:
            raise RuntimeError(f"Base de datos no soportada: {self.database_url}")

        connection = pymysql.connect(**self._connection_kwargs(include_database=True))
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def init_schema(self):
        """Inicializa el esquema de alertas para el analizador de riesgo."""
        self._create_database_if_missing()

        connection = pymysql.connect(**self._connection_kwargs(include_database=True))
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                for statement in self._schema_statements():
                    cursor.execute(statement)
                self._ensure_alerts_schema(cursor)
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            connection.commit()
        finally:
            connection.close()

    def _create_database_if_missing(self):
        connection = pymysql.connect(**self._connection_kwargs(include_database=False))
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.database_name}` DEFAULT CHARACTER SET utf8mb4"
                )
            connection.commit()
        finally:
            connection.close()

    def _schema_statements(self) -> list[str]:
        return [
            self._alerts_schema_sql(),
        ]

    def _alerts_schema_sql(self) -> str:
        return """
            CREATE TABLE IF NOT EXISTS alerts (
                id_alert INT NOT NULL AUTO_INCREMENT,
                alert_type VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                dhl_id VARCHAR(100) NOT NULL,
                id_shipment INT NOT NULL,
                current_location INT NULL,
                id_user INT NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                trigger_status VARCHAR(100) NULL,
                previous_status VARCHAR(100) NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'UNREAD',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (id_alert),
                INDEX idx_user_created (id_user, created_at),
                INDEX idx_dhl_id (dhl_id),
                INDEX idx_shipment (id_shipment),
                INDEX idx_alert_type (alert_type)
            ) ENGINE=InnoDB
        """

    def _ensure_alerts_schema(self, cursor):
        required_columns = {
            "dhl_id": "ALTER TABLE alerts ADD COLUMN dhl_id VARCHAR(100) NOT NULL DEFAULT '' AFTER description",
            "id_user": "ALTER TABLE alerts ADD COLUMN id_user INT NOT NULL DEFAULT 0 AFTER current_location",
            "user_email": "ALTER TABLE alerts ADD COLUMN user_email VARCHAR(255) NOT NULL DEFAULT '' AFTER id_user",
            "trigger_status": "ALTER TABLE alerts ADD COLUMN trigger_status VARCHAR(100) NULL AFTER user_email",
            "previous_status": "ALTER TABLE alerts ADD COLUMN previous_status VARCHAR(100) NULL AFTER trigger_status",
        }

        for column_name, statement in required_columns.items():
            if not self._column_exists(cursor, "alerts", column_name):
                cursor.execute(statement)

        cursor.execute(
            "ALTER TABLE alerts MODIFY COLUMN status VARCHAR(30) NOT NULL DEFAULT 'UNREAD'"
        )

        required_indexes = {
            "idx_user_created": "CREATE INDEX idx_user_created ON alerts (id_user, created_at)",
            "idx_dhl_id": "CREATE INDEX idx_dhl_id ON alerts (dhl_id)",
        }

        for index_name, statement in required_indexes.items():
            if not self._index_exists(cursor, "alerts", index_name):
                cursor.execute(statement)

    def _column_exists(self, cursor, table_name: str, column_name: str) -> bool:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
              AND column_name = %s
            """,
            (self.database_name, table_name, column_name),
        )
        return cursor.fetchone()["total"] > 0

    def _index_exists(self, cursor, table_name: str, index_name: str) -> bool:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM information_schema.statistics
            WHERE table_schema = %s
              AND table_name = %s
              AND index_name = %s
            """,
            (self.database_name, table_name, index_name),
        )
        return cursor.fetchone()["total"] > 0

database = Database(settings.DATABASE_URL)

def init_db():
    database.init_schema()
