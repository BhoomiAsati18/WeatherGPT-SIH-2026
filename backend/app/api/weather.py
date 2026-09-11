from fastapi import APIRouter, Query
from typing import Optional
from ..models.schemas import WeatherCardData, NWPComparisonResponse
from ..services.geocoding_service import resolve_location
from ..services.weather_service import fetch_weather_forecast, fetch_nwp_comparison
from ..services.alert_service import evaluate_disaster_alerts

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])

@router.get("/forecast", response_model=WeatherCardData)
async def get_forecast(
    location: Optional[str] = Query(None, description="City or district name"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude")
):
    """Retrieves live weather conditions, hourly and 7-day forecasts."""
    resolved_name = "New Delhi"
    admin1 = "Delhi"

    if location:
        geo = await resolve_location(location)
        if geo:
            lat = geo["latitude"]
            lon = geo["longitude"]
            resolved_name = geo["name"]
            admin1 = geo.get("admin1", "")
    elif lat is None or lon is None:
        lat, lon = 28.6139, 77.2090

    weather = await fetch_weather_forecast(lat, lon, resolved_name, admin1)
    weather.severe_warning = evaluate_disaster_alerts(weather, location or resolved_name)
    return weather

@router.get("/models", response_model=NWPComparisonResponse)
async def get_nwp_comparison(
    location: Optional[str] = Query("Indore", description="City or district name")
):
    """Compares ECMWF, GFS, and ICON Numerical Weather Prediction models side-by-side."""
    geo = await resolve_location(location)
    lat = geo["latitude"] if geo else 22.7196
    lon = geo["longitude"] if geo else 75.8577
    name = geo["name"] if geo else location

    comp = await fetch_nwp_comparison(lat, lon, name)
    return NWPComparisonResponse(**comp)
