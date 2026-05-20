from fastapi import APIRouter

from src.services.tracker_client import TrackerClient

router = APIRouter(
    prefix="/risk",
    tags=["Risk Analyzer"]
)


@router.get("/test/{tracking_id}")
async def test_connection(tracking_id: str):

    data = await TrackerClient.get_tracking_status(
        tracking_id
    )

    return data