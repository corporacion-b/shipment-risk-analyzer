from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Risk Analyzer API"
    DATABASE_URL: str = "mysql://root:secret@127.0.0.1:3306/risk_analysis"
    SHIPMENT_TRACKER_BASE_URL: str = "http://localhost:8000"
    JWT_SECRET_KEY: str = "change-this-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()