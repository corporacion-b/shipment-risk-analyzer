import asyncio

from src.schemas.tracking import AlertEvaluationRequest
from src.services.risk_service import RiskService


class FakeTrackerClient:
    async def fetch_current_user(self, token: str) -> dict:
        return {"id_user": 1, "email": "user@example.com"}


class FakeAlertRepository:
    def __init__(self):
        self.created_alerts = []

    def alert_exists(self, **kwargs) -> bool:
        return False

    def create_alert(self, **kwargs) -> dict:
        alert = {
            "id_alert": len(self.created_alerts) + 1,
            "created_at": "2026-05-31 00:00:00",
            "updated_at": "2026-05-31 00:00:00",
            **kwargs,
        }
        self.created_alerts.append(alert)
        return alert


def test_exception_status_creates_alert_without_previous_status():
    service = RiskService()
    service.tracker_client = FakeTrackerClient()
    service.alert_repo = FakeAlertRepository()

    result = asyncio.run(
        service.evaluate_shipment_update(
            AlertEvaluationRequest(
                dhl_id="N4X7B1K9YD",
                id_shipment=10,
                previous_status=None,
                current_status="Exception",
            ),
            "token",
        )
    )

    assert result["alerts_created"] == 1
    assert result["alerts"][0]["alert_type"] == "SHIPMENT_EXCEPTION"
    assert result["alerts"][0]["status"] == "UNREAD"


def test_regular_status_without_previous_status_does_not_create_status_alert():
    service = RiskService()
    service.tracker_client = FakeTrackerClient()
    service.alert_repo = FakeAlertRepository()

    result = asyncio.run(
        service.evaluate_shipment_update(
            AlertEvaluationRequest(
                dhl_id="L2N8Y4D6KP",
                id_shipment=11,
                previous_status=None,
                current_status="In transit",
                dwell_time_days=1,
                max_days_stopped=3,
            ),
            "token",
        )
    )

    assert result["alerts_created"] == 0
