from pydantic import BaseModel, Field
from typing import Optional
from typing import Literal


class AlertEvaluationRequest(BaseModel):
    dhl_id: str
    id_shipment: int
    previous_status: Optional[str] = None
    current_status: str
    current_location: Optional[int] = None
    dwell_time_days: Optional[float] = None
    max_days_stopped: int = 3


class AlertRead(BaseModel):
    id_alert: int
    alert_type: str
    description: str
    dhl_id: str
    id_shipment: int
    current_location: Optional[int] = None
    id_user: int
    user_email: str
    trigger_status: Optional[str] = None
    previous_status: Optional[str] = None
    status: str
    created_at: str
    updated_at: str


class AlertEvaluationResponse(BaseModel):
    alerts_created: int
    alerts: list[AlertRead]


class AlertListResponse(BaseModel):
    items: list[AlertRead]
    total: int


class AlertStatusUpdate(BaseModel):
    status: Literal["READ", "UNREAD"]


class AlertMarkReadRequest(BaseModel):
    alert_ids: list[int] = Field(default_factory=list)


class AlertMutationResponse(BaseModel):
    updated: int = 0
    deleted: int = 0
    dismissed: int = 0
