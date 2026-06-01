from src.services.tracker_client import TrackerClient
from src.repositories.alert_repository import AlertRepository
from src.schemas.tracking import AlertEvaluationRequest

class RiskService:
    def __init__(self):
        self.tracker_client = TrackerClient()
        self.alert_repo = AlertRepository()

    async def evaluate_shipment_update(self, payload: AlertEvaluationRequest, token: str) -> dict:
        current_user = await self.tracker_client.fetch_current_user(token)
        alerts = []

        previous_status = self._normalize_text(payload.previous_status)
        current_status = self._normalize_text(payload.current_status)
        status_changed = bool(previous_status) and previous_status != current_status
        should_create_status_alert = status_changed or self._is_notifiable_status(current_status)

        if should_create_status_alert:
            alert_type, description = self._status_alert(payload.dhl_id, payload.previous_status, payload.current_status)
            alert = self._create_internal_alert(
                alert_type=alert_type,
                description=description,
                dhl_id=payload.dhl_id,
                id_shipment=payload.id_shipment,
                current_location=payload.current_location,
                current_user=current_user,
                trigger_status=payload.current_status,
                previous_status=payload.previous_status,
            )
            if alert is not None:
                alerts.append(alert)

        if (
            payload.dwell_time_days is not None
            and payload.dwell_time_days >= payload.max_days_stopped
            and current_status != "delivered"
        ):
            description = (
                f"El paquete {payload.dhl_id} lleva {payload.dwell_time_days:.2f} dias "
                "sin avanzar desde su ubicacion actual."
            )
            alert = self._create_internal_alert(
                alert_type="DELAYED_IN_LOCATION",
                description=description,
                dhl_id=payload.dhl_id,
                id_shipment=payload.id_shipment,
                current_location=payload.current_location,
                current_user=current_user,
                trigger_status="DELAYED_IN_LOCATION",
                previous_status=payload.previous_status,
            )
            if alert is not None:
                alerts.append(alert)

        return {
            "alerts_created": len(alerts),
            "alerts": alerts,
        }

    @staticmethod
    def _normalize_text(value) -> str:
        if value is None:
            return ""

        return str(value).lower().strip()

    @classmethod
    def _is_notifiable_status(cls, status: str) -> bool:
        normalized_status = cls._normalize_text(status)
        return (
            "delivered" in normalized_status
            or "out for delivery" in normalized_status
            or "out_for_delivery" in normalized_status
            or "exception" in normalized_status
            or "hold" in normalized_status
        )

    @classmethod
    def _status_alert(cls, dhl_id: str, previous_status: str | None, current_status: str) -> tuple[str, str]:
        normalized_status = cls._normalize_text(current_status)

        if "delivered" in normalized_status:
            return "DELIVERED", f"El paquete {dhl_id} cambio de {previous_status} a entregado."

        if "out for delivery" in normalized_status or "out_for_delivery" in normalized_status:
            return "NEAR_DELIVERY", f"El paquete {dhl_id} salio a reparto."

        if "exception" in normalized_status or "hold" in normalized_status:
            return "SHIPMENT_EXCEPTION", f"El paquete {dhl_id} presenta una excepcion: {current_status}."

        return "STATUS_CHANGED", f"El paquete {dhl_id} cambio de {previous_status} a {current_status}."

    def _create_internal_alert(
        self,
        alert_type: str,
        description: str,
        dhl_id: str,
        id_shipment: int,
        current_location: int | None,
        current_user: dict,
        trigger_status: str | None,
        previous_status: str | None,
    ) -> dict | None:
        if self.alert_repo.alert_exists(
            id_user=current_user["id_user"],
            dhl_id=dhl_id,
            alert_type=alert_type,
            trigger_status=trigger_status,
        ):
            return None

        return self.alert_repo.create_alert(
            alert_type=alert_type,
            description=description,
            dhl_id=dhl_id,
            id_shipment=id_shipment,
            current_location=current_location,
            id_user=current_user["id_user"],
            user_email=current_user["email"],
            trigger_status=trigger_status,
            previous_status=previous_status,
            status="UNREAD",
        )
