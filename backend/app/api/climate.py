from fastapi import APIRouter, Query
from ..models.schemas import ClimateTrendResponse
from ..services.geocoding_service import resolve_location
from ..services.climate_service import fetch_climate_history

router = APIRouter(prefix="/climate", tags=["Climate Information & Historical Trends"])

@router.get("/history", response_model=ClimateTrendResponse)
async def get_climate_history(
    location: str = Query("Indore", description="District or city name")
):
    """
    Returns multi-year climate analysis and rainfall trends for agricultural planners and researchers.
    """
    geo = await resolve_location(location)
    lat = geo["latitude"] if geo else 22.7196
    lon = geo["longitude"] if geo else 75.8577
    name = geo["name"] if geo else location

    return await fetch_climate_history(lat, lon, name)
