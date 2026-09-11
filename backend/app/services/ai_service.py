import re
import os
from typing import Dict, Any, Tuple, Optional
from ..models.schemas import (
    WeatherCardData,
    AlertItem,
    PersonaType,
    LanguageType,
)
from ..config import settings

# Supported Indian cities regex
KNOWN_LOCATIONS = [
    "indore", "bhopal", "delhi", "new delhi", "mumbai", "pune", "jaipur",
    "lucknow", "patna", "kolkata", "bengaluru", "bangalore", "chennai",
    "hyderabad", "ahmedabad", "chandigarh", "varanasi", "kanpur", "nagpur",
    "surat", "visakhapatnam", "shimla", "dehradun", "srinagar", "goa", "udaipur",
    "jodhpur", "amritsar", "agra", "gwalior", "jabalpur", "ujjain"
]

def parse_user_query(message: str) -> Dict[str, Any]:
    """
    Parses intent, location, time, and language from the user query.
    """
    lower = message.lower()
    
    # Detect language
    lang = LanguageType.HINGLISH
    # Check Devanagari script for pure Hindi
    if re.search(r'[\u0900-\u097F]', message):
        lang = LanguageType.HINDI
    elif any(w in lower for w in ["will it", "what is", "temperature in", "forecast for", "should i", "heavy rain in"]):
        lang = LanguageType.ENGLISH

    # Detect Location
    detected_location = None
    for city in KNOWN_LOCATIONS:
        if re.search(rf"\b{city}\b", lower):
            detected_location = city.title()
            break

    # If not found, look for patterns like "in <word>", "me <word>", "ka <word>"
    if not detected_location:
        m = re.search(r"(?:in|at|me|mein|sheher|city)\s+([a-zA-Z]+)", lower)
        if m and m.group(1) not in ["kal", "aaj", "rain", "baarish", "weather", "delhi"]:
            detected_location = m.group(1).title()

    # Detect Time
    timeframe = "today"
    if any(w in lower for w in ["kal", "tomorrow", "agli subah", "next day"]):
        timeframe = "tomorrow"
    elif any(w in lower for w in ["weekend", "sunday", "hafta", "week", "7 days", "agale din"]):
        timeframe = "7_days"

    # Detect Intent
    intent = "general_forecast"
    if any(w in lower for w in ["alert", "warning", "khatra", "cyclone", "toofan", "tsunami", "flood", "baad"]):
        intent = "disaster_alert"
    elif any(w in lower for w in ["irrigate", "sinchai", "paani", "crop", "fasal", "khet", "kisan", "spray", "pesticide"]):
        intent = "agriculture"
    elif any(w in lower for w in ["travel", "safar", "jaana", "drive", "road", "flight", "highway"]):
        intent = "travel"
    elif any(w in lower for w in ["baarish", "rain", "raining", "barsat"]):
        intent = "rain_forecast"
    elif any(w in lower for w in ["garmi", "heat", "temperature", "temp", "cold", "sardi", "humid"]):
        intent = "temperature"
    elif any(w in lower for w in ["history", "trend", "climate", "pichle saal", "average"]):
        intent = "climate_history"

    return {
        "location": detected_location,
        "timeframe": timeframe,
        "intent": intent,
        "detected_language": lang
    }

async def generate_conversational_response(
    query: str,
    parsed: Dict[str, Any],
    weather: WeatherCardData,
    alert: Optional[AlertItem],
    advisories: list,
    persona: PersonaType,
    lang: LanguageType
) -> str:
    """
    Synthesizes a human-friendly, authoritative explanation.
    Uses Gemini API if key is provided, or the built-in grounded NLU engine.
    """
    # 1. Try Google Gemini if configured
    gemini_key = settings.GEMINI_API_KEY.strip()
    if gemini_key:
        try:
            return await _call_gemini_llm(
                query, parsed, weather, alert, advisories, persona, lang, gemini_key
            )
        except Exception as e:
            print(f"Gemini API call failed ({e}), falling back to internal NLU generator.")

    # 2. Built-in Grounded Meteorological NLU Engine
    return _generate_grounded_fallback(
        query, parsed, weather, alert, advisories, persona, lang
    )

def _generate_grounded_fallback(
    query: str,
    parsed: Dict[str, Any],
    weather: WeatherCardData,
    alert: Optional[AlertItem],
    advisories: list,
    persona: PersonaType,
    lang: LanguageType
) -> str:
    loc = weather.location
    timeframe = parsed.get("timeframe", "today")
    rain_prob = weather.precipitation_probability
    temp = weather.temperature
    condition = weather.condition
    time_label = "Kal" if timeframe == "tomorrow" else "Aaj"
    time_label_en = "Tomorrow" if timeframe == "tomorrow" else "Today"

    # Alert context
    alert_prefix = ""
    if alert and alert.severity.value in ["warning", "severe"]:
        if lang == LanguageType.HINDI:
            alert_prefix = f"🚨 **चेतावनी ({alert.category}):** {alert.headline}!\n\n"
        elif lang == LanguageType.HINGLISH:
            alert_prefix = f"🚨 **ALERT ({alert.category}):** {alert.headline}!\n\n"
        else:
            alert_prefix = f"🚨 **OFFICIAL ALERT ({alert.category}):** {alert.headline}!\n\n"

    # Specific responses based on language
    if lang == LanguageType.HINDI:
        if parsed["intent"] == "rain_forecast":
            if rain_prob > 60:
                body = f"हाँ, {loc} में {time_label.lower()} बारिश होने की **प्रबल संभावना ({rain_prob}%)** है। वर्तमान मौसम {condition} है और तापमान लगभग {temp}°C बना हुआ है।"
            elif rain_prob > 30:
                body = f"{loc} में {time_label.lower()} हल्की बूंदाबांदी या छिटपुट बारिश की संभावना ({rain_prob}%) है। तापमान {temp}°C के आसपास रहेगा।"
            else:
                body = f"{loc} में {time_label.lower()} बारिश की संभावना काफी कम ({rain_prob}%) है। मौसम मुख्य रूप से {condition} रहेगा और तापमान लगभग {temp}°C रहेगा।"
        elif parsed["intent"] == "disaster_alert":
            if alert:
                body = f"{loc} के लिए {alert.headline} सक्रिय है। {alert.description}"
            else:
                body = f"{loc} के लिए वर्तमान में कोई गंभीर मौसम चेतावनी सक्रिय नहीं है। स्थितियां सामान्य और नियंत्रण में हैं।"
        else:
            body = f"{loc} में {time_label.lower()} का मौसम {condition} बना हुआ है। वर्तमान तापमान {temp}°C (अनुभूत: {weather.apparent_temperature}°C), आर्द्रता {weather.humidity}% और हवा की गति {weather.wind_speed} km/h है।"

    elif lang == LanguageType.HINGLISH:
        if parsed["intent"] == "rain_forecast":
            if rain_prob > 60:
                body = f"Haan, {loc} mein {time_label.lower()} baarish hone ke **kaafi acche chances ({rain_prob}%)** hain! Current condition {condition} hai aur temperature {temp}°C ke aas-paas hai."
            elif rain_prob > 30:
                body = f"{loc} mein {time_label.lower()} thodi bahut boonda-baandi ya light shower ki possibility ({rain_prob}%) hai. Mausam {condition} rahega aur temperature around {temp}°C rahega."
            else:
                body = f"{loc} mein {time_label.lower()} baarish ki possibility kaafi kam ({rain_prob}%) hai. Aasman mostly {condition} rahega aur maximum temperature {temp}°C tak jayega."
        elif parsed["intent"] == "disaster_alert":
            if alert:
                body = f"{loc} ke liye **{alert.headline}** active hai. {alert.description}"
            else:
                body = f"{loc} ke liye abhi koi severe disaster alert ya emergency warning active nahi hai. Weather condition normal hai."
        else:
            body = f"{loc} mein {time_label.lower()} mausam {condition} rahega. Current temperature **{temp}°C** (feels like {weather.apparent_temperature}°C), humidity {weather.humidity}% aur wind speed {weather.wind_speed} km/h hai."

    else: # ENGLISH
        if parsed["intent"] == "rain_forecast":
            if rain_prob > 60:
                body = f"Yes, there is a **high probability of rain ({rain_prob}%)** in {loc} {time_label_en.lower()}. Expect {condition} with temperatures around {temp}°C."
            elif rain_prob > 30:
                body = f"There is a moderate chance of isolated light showers ({rain_prob}%) in {loc} {time_label_en.lower()}. The sky condition will remain {condition} with a temperature of {temp}°C."
            else:
                body = f"Rainfall is unlikely in {loc} {time_label_en.lower()} with only a {rain_prob}% probability. Skies will be {condition} with temperatures around {temp}°C."
        elif parsed["intent"] == "disaster_alert":
            if alert:
                body = f"Active weather warning for {loc}: **{alert.headline}**. {alert.description}"
            else:
                body = f"No severe weather warnings or disaster alerts are currently active for {loc}. Meteorological indices remain in the green zone."
        else:
            body = f"The weather in {loc} {time_label_en.lower()} is {condition}. Currently, the temperature is **{temp}°C** (apparent {weather.apparent_temperature}°C), relative humidity is {weather.humidity}%, and winds are blowing at {weather.wind_speed} km/h."

    # Append persona tip if present
    tip_str = ""
    if advisories:
        tip_str = "\n\n💡 **Actionable Tip:**\n• " + "\n• ".join(advisories[:2])

    return f"{alert_prefix}{body}{tip_str}"

async def _call_gemini_llm(
    query: str,
    parsed: Dict[str, Any],
    weather: WeatherCardData,
    alert: Optional[AlertItem],
    advisories: list,
    persona: PersonaType,
    lang: LanguageType,
    api_key: str
) -> str:
    """Invokes Google Gemini API with grounded constraints."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    system_prompt = (
        "You are WeatherGPT, an authoritative conversational meteorological AI platform developed for "
        "Smart India Hackathon (SIH26068) under the Ministry of Earth Sciences (MoES) and IMD.\n"
        "STRICT GROUNDING RULE: You must ONLY communicate the verified meteorological and alert facts provided in the prompt. "
        "NEVER hallucinate, invent, or speculate any temperature, rain percentage, or wind metrics.\n"
        f"Target Persona: {persona.value.upper()}\n"
        f"Language requested: {lang.value.upper()} (Respond naturally in Hindi, Hinglish, or English as requested).\n"
        "Keep answers concise, direct, empathetic, and actionable."
    )

    data_payload = {
        "location": weather.location,
        "temperature_celsius": weather.temperature,
        "apparent_temperature": weather.apparent_temperature,
        "weather_condition": weather.condition,
        "precipitation_probability": weather.precipitation_probability,
        "humidity_percent": weather.humidity,
        "wind_speed_kmh": weather.wind_speed,
        "active_alert": alert.model_dump() if alert else None,
        "advisories": advisories
    }

    prompt = (
        f"User Query: \"{query}\"\n\n"
        f"Verified Meteorological Data:\n{data_payload}\n\n"
        f"Provide a natural, helpful, grounded response in {lang.value} with clear actionable advice."
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
        )
    )
    return response.text
