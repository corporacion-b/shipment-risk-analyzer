from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.tracking import DelayAnalysisRequest, AlertAnalysisResponse
from src.services.risk_service import RiskService

router = APIRouter(prefix="/tracking", tags=["Tracking Risk Analysis"])

security_scheme = HTTPBearer()

def get_token_from_header(credenciales: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """Extrae el token de forma nativa desde las cabeceras HTTP."""
    return credenciales.credentials

@router.post(
    "/analyze-delay/{dhl_id}", 
    response_model=AlertAnalysisResponse, 
    status_code=status.HTTP_200_OK
)
async def analyze_delay(
    dhl_id: str,
    payload: DelayAnalysisRequest,
    token: str = Depends(get_token_from_header),
    risk_service: RiskService = Depends()
):
    return await risk_service.analyze_delay_risk(
        dhl_id=dhl_id, 
        max_days_stopped=payload.max_days_stopped, 
        token=token
    )