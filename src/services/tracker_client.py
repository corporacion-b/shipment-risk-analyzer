import httpx


class TrackerClient:

    BASE_URL = "http://localhost:8000"

    @classmethod
    async def get_tracking_status(cls, tracking_id: str):

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{cls.BASE_URL}/status/{tracking_id}"
            )

            response.raise_for_status()

            return response.json()