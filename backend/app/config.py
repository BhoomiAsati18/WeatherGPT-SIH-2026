import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "WeatherGPT"
    API_V1_STR: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Gemini LLM (optional, system has built-in offline NLU if key is absent)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # CORS
    ALLOWED_ORIGINS: str = "*"

    # Default Indian city if none specified
    DEFAULT_CITY: str = "New Delhi"
    DEFAULT_LAT: float = 28.6139
    DEFAULT_LON: float = 77.2090

    # Cache TTL in seconds
    CACHE_TTL_SECONDS: int = 900

    @property
    def cors_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
