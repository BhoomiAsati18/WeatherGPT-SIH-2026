from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PersonaType(str, Enum):
    FARMER = "farmer"          # 🌾 Kisan - Agro advisories, irrigation, spraying
    TRAVELER = "traveler"      # ✈️ Yatri - Road visibility, flights, hydroplaning
    CITIZEN = "citizen"        # 🏙️ Nagrik - Daily commuting, heat/UV, umbrella
    DISASTER_OFFICER = "disaster_officer" # 🚨 Disaster Manager - Evacuation, severe warning summary

class LanguageType(str, Enum):
    HINDI = "hindi"
    HINGLISH = "hinglish"
    ENGLISH = "english"

class AlertSeverity(str, Enum):
    NORMAL = "normal"
    WATCH = "watch"        # Yellow
    WARNING = "warning"    # Orange
    SEVERE = "severe"      # Red

class AlertItem(BaseModel):
    severity: AlertSeverity = AlertSeverity.NORMAL
    category: str = "Weather"
    headline: str
    description: str
    instructions: List[str] = []
    source: str = "NDMA SACHET / IMD Early Warning"
    color_hex: str = "#22c55e" # Green by default

class HourlyPoint(BaseModel):
    time: str
    temperature: float
    precipitation_probability: int
    weather_code: int
    condition: str

class DailyForecast(BaseModel):
    date: str
    max_temp: float
    min_temp: float
    precipitation_probability: int
    weather_code: int
    condition: str

class WeatherCardData(BaseModel):
    location: str
    state_or_country: Optional[str] = None
    latitude: float
    longitude: float
    temperature: float
    apparent_temperature: float
    condition: str
    weather_code: int
    humidity: int
    wind_speed: float
    wind_direction: int
    uv_index: float
    precipitation: float
    precipitation_probability: int
    air_quality_index: Optional[int] = 45
    severe_warning: Optional[AlertItem] = None
    hourly: List[HourlyPoint] = []
    daily: List[DailyForecast] = []

class ChatRequest(BaseModel):
    message: str = Field(..., description="User question in natural language (Hindi, English, or Hinglish)")
    conversation_id: Optional[str] = None
    persona: PersonaType = PersonaType.CITIZEN
    language: LanguageType = LanguageType.HINGLISH
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    persona: PersonaType
    language: LanguageType
    extracted_location: str
    extracted_intent: str
    weather_card: Optional[WeatherCardData] = None
    alert: Optional[AlertItem] = None
    actionable_advisory: List[str] = []
    suggested_followups: List[str] = []
    sources: List[str] = ["Open-Meteo NWP", "IMD/NDMA Criteria"]

class NWPComparisonResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    models: Dict[str, Any]
    consensus_summary: str

class ClimateTrendResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    historical_years: List[int]
    annual_rainfall_mm: List[float]
    average_max_temp: List[float]
    summary_analysis: str
