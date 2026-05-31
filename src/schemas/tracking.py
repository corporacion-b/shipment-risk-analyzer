from pydantic import BaseModel
from typing import Optional


class DelayAnalysisRequest(BaseModel):
    max_days_stopped: int = 3


class AlertAnalysisResponse(BaseModel):
    alert_generated: bool
    days_stopped: int
    message: str
    detail: Optional[str] = None


class ShipmentAlertResponse(BaseModel):
    alert_generated: bool
    message: str
    detail: Optional[str] = None
    tracker_status: Optional[str] = None