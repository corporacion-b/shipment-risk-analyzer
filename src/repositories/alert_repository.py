from src.db.connection import database

class AlertRepository:
    def create_alert(self, alert_type: str, description: str, id_shipment: int, current_location: int, status: str = "SENT") -> bool:
        """Inserta de manera segura una nueva alerta en la base de datos local."""
        query = """
            INSERT INTO alerts (alert_type, description, id_shipment, current_location, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (alert_type, description, id_shipment, current_location, status))
        return True