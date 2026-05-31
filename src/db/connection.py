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
                
                -- IDs lógicos de referencia a tu otra API (Tracker)
                id_shipment INT NOT NULL,
                current_location INT NOT NULL,
                
                -- Estado del procesamiento (ej. PENDIENTE, ENVIADA)
                status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
                
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (id_alert),
                INDEX idx_shipment (id_shipment),
                INDEX idx_alert_type (alert_type)
            ) ENGINE=InnoDB
        """

database = Database(settings.DATABASE_URL)

def init_db():
    database.init_schema()