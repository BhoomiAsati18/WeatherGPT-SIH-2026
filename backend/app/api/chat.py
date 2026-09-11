from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatRequest, ChatResponse, PersonaType, LanguageType
from ..services.geocoding_service import resolve_location
from ..services.weather_service import fetch_weather_forecast
from ..services.alert_service import evaluate_disaster_alerts
from ..services.advisory_engine import generate_persona_advisories
from ..services.ai_service import parse_user_query, generate_conversational_response

router = APIRouter(prefix="/chat", tags=["Conversational AI"])

@router.post("", response_model=ChatResponse)
async def chat_interaction(req: ChatRequest):
    """
    Main Conversational Weather & Disaster Intelligence Endpoint.
    Orchestrates: Query understanding -> Geocoding -> Weather NWP -> Alerts -> Persona Advisory -> Conversational Synthesis.
    """
    query_text = req.message.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    # 1. Parse Query (Intent, Location, Timeframe, Language)
    parsed = parse_user_query(query_text)
    
    # User's explicit language preference takes precedence if supplied
    effective_lang = req.language or parsed.get("detected_language", LanguageType.HINGLISH)
    effective_persona = req.persona or PersonaType.CITIZEN

    # 2. Location Resolution
    target_city = req.city or parsed.get("location")
    lat, lon = req.latitude, req.longitude
    resolved_name = "New Delhi"
    admin1 = "Delhi"

    if target_city:
        geo = await resolve_location(target_city)
        if geo:
            lat = geo["latitude"]
            lon = geo["longitude"]
            resolved_name = geo["name"]
            admin1 = geo.get("admin1", "")
    elif lat is not None and lon is not None:
        resolved_name = f"Coordinates ({lat:.2f}, {lon:.2f})"
    else:
        # Default to Delhi
        geo = await resolve_location("Delhi")
        if geo:
            lat, lon = geo["latitude"], geo["longitude"]
            resolved_name = geo["name"]

    # 3. Retrieve Live Weather Data & NWP Forecast
    weather_card = await fetch_weather_forecast(lat, lon, resolved_name, admin1)

    # 4. Evaluate Disaster Warning / Alerts
    alert_item = evaluate_disaster_alerts(weather_card, target_city or resolved_name)
    weather_card.severe_warning = alert_item

    # 5. Generate Domain Persona Advisories
    advisories = generate_persona_advisories(weather_card, effective_persona, effective_lang)

    # 6. Generate Grounded AI Response
    answer_text = await generate_conversational_response(
        query=query_text,
        parsed=parsed,
        weather=weather_card,
        alert=alert_item,
        advisories=advisories,
        persona=effective_persona,
        lang=effective_lang
    )

    # Dynamic follow-up suggestion chips
    followups = [
        f"{resolved_name} agale 3 din ka forecast?",
        f"Kya {resolved_name} me koi active warning hai?",
        "Kheti ke liye irrigation kab sahi rahegi?",
    ]

    return ChatResponse(
        answer=answer_text,
        persona=effective_persona,
        language=effective_lang,
        extracted_location=resolved_name,
        extracted_intent=parsed.get("intent", "general_forecast"),
        weather_card=weather_card,
        alert=alert_item,
        actionable_advisory=advisories,
        suggested_followups=followups,
        sources=["Open-Meteo ECMWF/GFS", "IMD Alert Criteria", "NDMA SACHET"]
    )
