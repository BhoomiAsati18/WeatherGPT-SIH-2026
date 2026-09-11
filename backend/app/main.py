from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api import chat, weather, alerts, climate

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Conversational AI for Weather Forecasting, Alerts, and Climate Information (SIH26068)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(weather.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(climate.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "WeatherGPT SIH26068 API",
        "docs": "/docs",
        "endpoints": {
            "chat": f"{settings.API_V1_STR}/chat",
            "weather": f"{settings.API_V1_STR}/weather/forecast",
            "models": f"{settings.API_V1_STR}/weather/models",
            "alerts": f"{settings.API_V1_STR}/alerts/active",
            "climate": f"{settings.API_V1_STR}/climate/history"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
