from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import tracking
from src.core.config import settings
from src.db.connection import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


src = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

frontend_origins = [
    origin.strip()
    for origin in settings.FRONTEND_ORIGINS.split(",")
    if origin.strip()
]

src.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
src.include_router(tracking.router)

@src.get("/", tags=["General"])
async def health():
    """Revisar estado de la API."""
    return {"service": settings.PROJECT_NAME, "status": "online"}
