from datetime import datetime, timezone
from fastapi import HTTPException
from src.services.tracker_client import TrackerClient
from src.repositories.alert_repository import AlertRepository
from src.db.connection import database
from src.schemas.tracking import ShipmentAlertResponse

class RiskService:
    def __init__(self):
        self.tracker_client = TrackerClient()
        self.alert_repo = AlertRepository()

    async def analyze_delay_risk(self, dhl_id: str, max_days_stopped: int, token: str) -> dict:
        # Consultar los datos físicos viejos en la tabla vecina ANTES de llamar al Tracker
        query = """
            SELECT id_shipment, current_location, updated_at 
            FROM shipments.shipments 
            WHERE dhl_id = %s
        """
        
        db_data = None
        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (dhl_id,))
                db_data = cursor.fetchone()

        if not db_data:
            raise HTTPException(status_code=404, detail="Paquete no encontrado en los registros físicos de la BD.")

        id_shipment = db_data["id_shipment"]
        current_location = db_data["current_location"]
        updated_at = db_data["updated_at"] 

        if not current_location:
            raise HTTPException(status_code=400, detail="El paquete no tiene una ubicación actual asignada.")

        # Calcular los días transcurridos usando la fecha previa al guardado
        if updated_at.tzinfo is not None:
            updated_at = updated_at.replace(tzinfo=None)
            
        now = datetime.now()
        days_stopped = abs((now - updated_at).days)

        # Validar con la Tracker API para actualizar el estado del paquete en el ecosistema
        tracker_data = await self.tracker_client.fetch_shipment(dhl_id, token)
        current_status = tracker_data.get("status")

        # Evaluar condición de riesgo con los días reales acumulados
        if days_stopped >= max_days_stopped and current_status.upper() != "DELIVERED":
            alert_type = "DELAYED_IN_LOCATION"
            description = f"El paquete {dhl_id} lleva {days_stopped} días detenido en la ubicación ID {current_location}."
            
            self.alert_repo.create_alert(
                alert_type=alert_type,
                description=description,
                id_shipment=id_shipment,
                current_location=current_location,
                status="SENT"
            )

            return {
                "alert_generated": True,
                "days_stopped": days_stopped,
                "message": "Alerta generada con éxito en el analizador de riesgos.",
                "detail": description
            }

        return {
            "alert_generated": False,
            "days_stopped": days_stopped,
            "message": f"El paquete opera dentro de los parámetros normales ({days_stopped} días)."
        }
    async def analyze_delivered_risk(self, dhl_id: str, token: str) -> ShipmentAlertResponse:
        query = """
            SELECT id_shipment, current_location, updated_at 
            FROM shipments.shipments 
            WHERE dhl_id = %s
        """

        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (dhl_id,))
                db_data = cursor.fetchone()

        if not db_data:
            raise HTTPException(
                status_code=404,
                detail="Paquete no encontrado en los registros físicos de la BD."
            )

        id_shipment = db_data["id_shipment"]
        current_location = db_data["current_location"]

        if not current_location:
            raise HTTPException(
                status_code=400,
                detail="El paquete no tiene una ubicación actual asignada."
            )

        tracker_data = await self.tracker_client.fetch_shipment(dhl_id, token)

        status = self._normalize_text(tracker_data.get("status"))
        description_text = self._normalize_text(tracker_data.get("description"))

        delivered_keywords = [
            "delivered",
            "entregado",
            "entregada",
            "shipment has been delivered",
            "delivery completed",
            "completed",
        ]

        is_delivered = self._contains_any(status, delivered_keywords) or self._contains_any(
            description_text,
            delivered_keywords
        )

        if is_delivered:
            alert_type = "DELIVERED"
            description = f"El paquete {dhl_id} ya fue entregado."

            self.alert_repo.create_alert(
                alert_type=alert_type,
                description=description,
                id_shipment=id_shipment,
                current_location=current_location,
                status="SENT"
            )

            return ShipmentAlertResponse(
                alert_generated=True,
                message="Alerta de entrega generada con éxito.",
                detail=description,
                tracker_status=tracker_data.get("status")
            )

        return ShipmentAlertResponse(
            alert_generated=False,
            message="El paquete todavía no ha sido entregado.",
            tracker_status=tracker_data.get("status")
        )

    async def analyze_near_delivery_risk(self, dhl_id: str, token: str) -> ShipmentAlertResponse:
        query = """
            SELECT id_shipment, current_location, updated_at 
            FROM shipments.shipments 
            WHERE dhl_id = %s
        """

        with database.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (dhl_id,))
                db_data = cursor.fetchone()

        if not db_data:
            raise HTTPException(
                status_code=404,
                detail="Paquete no encontrado en los registros físicos de la BD."
            )

        id_shipment = db_data["id_shipment"]
        current_location = db_data["current_location"]

        if not current_location:
            raise HTTPException(
                status_code=400,
                detail="El paquete no tiene una ubicación actual asignada."
            )

        tracker_data = await self.tracker_client.fetch_shipment(dhl_id, token)

        status = self._normalize_text(tracker_data.get("status"))
        description_text = self._normalize_text(tracker_data.get("description"))

        near_delivery_keywords = [
            "out_for_delivery",
            "out for delivery",
            "por entregar",
            "próximo a entregar",
            "proximo a entregar",
            "en reparto",
            "ready for delivery",
            "delivery soon",
            "near delivery",
        ]

        is_near_delivery = self._contains_any(status, near_delivery_keywords) or self._contains_any(
            description_text,
            near_delivery_keywords
        )

        if is_near_delivery:
            alert_type = "NEAR_DELIVERY"
            description = f"El paquete {dhl_id} está próximo a entregarse."

            self.alert_repo.create_alert(
                alert_type=alert_type,
                description=description,
                id_shipment=id_shipment,
                current_location=current_location,
                status="SENT"
            )

            return ShipmentAlertResponse(
                alert_generated=True,
                message="Alerta de próxima entrega generada con éxito.",
                detail=description,
                tracker_status=tracker_data.get("status")
            )

        return ShipmentAlertResponse(
            alert_generated=False,
            message="El paquete no está próximo a entregarse.",
            tracker_status=tracker_data.get("status")
        )

    @staticmethod
    def _normalize_text(value) -> str:
        if value is None:
            return ""

        return str(value).lower().strip()

    @staticmethod
    def _contains_any(text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)