from src.db.connection import database

class AlertRepository:
    def create_alert(
        self,
        alert_type: str,
        description: str,
        dhl_id: str,
        id_shipment: int,
        current_location: int | None,
        id_user: int,
        user_email: str,
        trigger_status: str | None = None,
        previous_status: str | None = None,
        status: str = "UNREAD",
    ) -> dict:
        query = """
            INSERT INTO alerts (
                alert_type, description, dhl_id, id_shipment,
                current_location, id_user, user_email, trigger_status,
                previous_status, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        alert_type,
                        description,
                        dhl_id,
                        id_shipment,
                        current_location,
                        id_user,
                        user_email,
                        trigger_status,
                        previous_status,
                        status,
                    ),
                )
                alert_id = cursor.lastrowid

        created = self.get_by_id(alert_id)
        if created is None:
            raise RuntimeError("No se pudo recuperar la alerta creada.")
        return created

    def list_for_user(self, id_user: int) -> dict:
        query = """
            SELECT
                id_alert,
                alert_type,
                description,
                dhl_id,
                id_shipment,
                current_location,
                id_user,
                user_email,
                trigger_status,
                previous_status,
                CASE WHEN status = 'UNREAD' THEN 'UNREAD' ELSE 'READ' END AS status,
                CAST(created_at AS CHAR) AS created_at,
                CAST(updated_at AS CHAR) AS updated_at
            FROM alerts
            WHERE id_user = %s
              AND status <> 'DISMISSED'
            ORDER BY created_at DESC, id_alert DESC
        """
        count_query = "SELECT COUNT(*) AS total FROM alerts WHERE id_user = %s AND status <> 'DISMISSED'"

        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (id_user,))
                items = cursor.fetchall()
                cursor.execute(count_query, (id_user,))
                total = cursor.fetchone()["total"]

        return {"items": items, "total": total}

    def get_by_id(self, alert_id: int) -> dict | None:
        query = """
            SELECT
                id_alert,
                alert_type,
                description,
                dhl_id,
                id_shipment,
                current_location,
                id_user,
                user_email,
                trigger_status,
                previous_status,
                CASE WHEN status = 'UNREAD' THEN 'UNREAD' ELSE 'READ' END AS status,
                CAST(created_at AS CHAR) AS created_at,
                CAST(updated_at AS CHAR) AS updated_at
            FROM alerts
            WHERE id_alert = %s
        """

        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (alert_id,))
                return cursor.fetchone()

    def alert_exists(
        self,
        id_user: int,
        dhl_id: str,
        alert_type: str,
        trigger_status: str | None,
    ) -> bool:
        query = """
            SELECT COUNT(*) AS total
            FROM alerts
            WHERE id_user = %s
              AND dhl_id = %s
              AND alert_type = %s
              AND (
                (trigger_status IS NULL AND %s IS NULL)
                OR trigger_status = %s
              )
        """
        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (id_user, dhl_id, alert_type, trigger_status, trigger_status))
                return cursor.fetchone()["total"] > 0

    def update_status(self, alert_id: int, id_user: int, status: str) -> dict | None:
        query = """
            UPDATE alerts
            SET status = %s
            WHERE id_alert = %s
              AND id_user = %s
        """
        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (status, alert_id, id_user))
                updated = cursor.rowcount

        if updated == 0:
            return None
        return self.get_by_id(alert_id)

    def mark_read(self, id_user: int, alert_ids: list[int]) -> int:
        if not alert_ids:
            return 0

        placeholders = ", ".join(["%s"] * len(alert_ids))
        query = f"""
            UPDATE alerts
            SET status = 'READ'
            WHERE id_user = %s
              AND status = 'UNREAD'
              AND id_alert IN ({placeholders})
        """
        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, [id_user, *alert_ids])
                return cursor.rowcount

    def dismiss_for_user(self, alert_id: int, id_user: int) -> int:
        query = """
            UPDATE alerts
            SET status = 'DISMISSED'
            WHERE id_alert = %s
              AND id_user = %s
        """
        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (alert_id, id_user))
                return cursor.rowcount

    def delete_by_shipment_for_user(self, dhl_id: str, id_user: int) -> int:
        query = """
            DELETE FROM alerts
            WHERE dhl_id = %s
              AND id_user = %s
        """
        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (dhl_id, id_user))
                return cursor.rowcount
