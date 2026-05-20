from fastapi import FastAPI

from api.routes.tracking import router as risk_router

app = FastAPI(
    title="Shipment Risk Analyzer API",
    version="1.0.0"
)

app.include_router(risk_router)