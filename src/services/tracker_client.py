import httpx
from fastapi import HTTPException, status
from src.core.config import settings

class TrackerClient:
    async def fetch_shipment(self, dhl_id: str, token: str) -> dict:
        """Consume la API tracker usando la URL raíz real sin prefijos."""
        url = f"{settings.SHIPMENT_TRACKER_BASE_URL}/status/{dhl_id}"
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=5.0)
                
                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    raise HTTPException(status_code=401, detail="Token inválido o expirado en el Tracker")
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    raise HTTPException(status_code=404, detail="El envío no existe en el Tracker")
                
                response.raise_for_status()
                return response.json()
                
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"No se pudo conectar con la API Tracker: {exc}"
                )