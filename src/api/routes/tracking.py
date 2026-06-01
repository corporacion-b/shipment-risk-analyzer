from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.tracking import (
    AlertEvaluationRequest,
    AlertEvaluationResponse,
    AlertMarkReadRequest,
    AlertMutationResponse,
    AlertListResponse,
    AlertRead,
    AlertStatusUpdate,
)
from src.repositories.alert_repository import AlertRepository
from src.services.tracker_client import TrackerClient
from src.services.risk_service import RiskService

router = APIRouter(prefix="/tracking", tags=["Tracking Risk Analysis"])

security_scheme = HTTPBearer()

def get_token_from_header(credenciales: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """Extrae el token de forma nativa desde las cabeceras HTTP."""
    return credenciales.credentials


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    token: str = Depends(get_token_from_header),
    tracker_client: TrackerClient = Depends(),
    alert_repository: AlertRepository = Depends(),
):
    current_user = await tracker_client.fetch_current_user(token)
    return alert_repository.list_for_user(current_user["id_user"])


@router.post("/evaluate", response_model=AlertEvaluationResponse)
async def evaluate_shipment_update(
    payload: AlertEvaluationRequest,
    token: str = Depends(get_token_from_header),
    risk_service: RiskService = Depends(),
):
    return await risk_service.evaluate_shipment_update(payload, token)


@router.patch("/alerts/{alert_id}", response_model=AlertRead)
async def update_alert_status(
    alert_id: int,
    payload: AlertStatusUpdate,
    token: str = Depends(get_token_from_header),
    tracker_client: TrackerClient = Depends(),
    alert_repository: AlertRepository = Depends(),
):
    current_user = await tracker_client.fetch_current_user(token)
    alert = alert_repository.update_status(alert_id, current_user["id_user"], payload.status)
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La notificacion no existe.",
        )
    return alert


@router.post("/alerts/mark-read", response_model=AlertMutationResponse)
async def mark_alerts_read(
    payload: AlertMarkReadRequest,
    token: str = Depends(get_token_from_header),
    tracker_client: TrackerClient = Depends(),
    alert_repository: AlertRepository = Depends(),
):
    current_user = await tracker_client.fetch_current_user(token)
    updated = alert_repository.mark_read(current_user["id_user"], payload.alert_ids)
    return AlertMutationResponse(updated=updated)


@router.delete("/alerts/{alert_id}", response_model=AlertMutationResponse)
async def delete_alert(
    alert_id: int,
    token: str = Depends(get_token_from_header),
    tracker_client: TrackerClient = Depends(),
    alert_repository: AlertRepository = Depends(),
):
    current_user = await tracker_client.fetch_current_user(token)
    dismissed = alert_repository.dismiss_for_user(alert_id, current_user["id_user"])
    if dismissed == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La notificacion no existe.",
        )
    return AlertMutationResponse(deleted=dismissed, dismissed=dismissed)


@router.delete("/alerts/by-shipment/{tracking_id}", response_model=AlertMutationResponse)
async def delete_alerts_by_shipment(
    tracking_id: str,
    token: str = Depends(get_token_from_header),
    tracker_client: TrackerClient = Depends(),
    alert_repository: AlertRepository = Depends(),
):
    current_user = await tracker_client.fetch_current_user(token)
    deleted = alert_repository.delete_by_shipment_for_user(tracking_id, current_user["id_user"])
    return AlertMutationResponse(deleted=deleted)
