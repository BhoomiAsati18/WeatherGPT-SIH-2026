from fastapi import APIRouter, Query
from typing import List, Optional
from ..models.schemas import AlertItem
from ..services.alert_service import REGIONAL_CAP_ALERTS
from ..services.geocoding_service import resolve_location
from ..services.weather_service import fetch_weather_forecast
from ..services.alert_service import evaluate_disaster_alerts

router = APIRouter(prefix="/alerts", tags=["Disaster Management Alerts"])

@router.get("/active", response_model=List[AlertItem])
async def get_all_active_alerts():
    """Returns currently active disaster alerts across key monitored districts."""
    alerts: List[AlertItem] = []
    for a in REGIONAL_CAP_ALERTS:
        alerts.append(
            AlertItem(
                severity=a["severity"],
                category=a["category"],
                headline=a["headline"],
                description=a["description"],
                instructions=a["instructions"],
                source=a["source"],
                color_hex=a["color_hex"]
            )
        )
    return alerts

@router.get("/check", response_model=Optional[AlertItem])
async def check_location_alert(
    location: str = Query("Indore", description="District or city name")
):
    """Evaluates disaster warning for a specific location."""
    geo = await resolve_location(location)
    lat = geo["latitude"] if geo else 22.7196
    lon = geo["longitude"] if geo else 75.8577
    name = geo["name"] if geo else location

    weather = await fetch_weather_forecast(lat, lon, name)
    return evaluate_disaster_alerts(weather, location)
