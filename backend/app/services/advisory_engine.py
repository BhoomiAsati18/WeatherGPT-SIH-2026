from typing import List
from ..models.schemas import WeatherCardData, PersonaType, LanguageType

def generate_persona_advisories(
    weather: WeatherCardData,
    persona: PersonaType,
    lang: LanguageType = LanguageType.HINGLISH
) -> List[str]:
    """
    Generates domain-specific, actionable advisories based on meteorological metrics.
    """
    advisories: List[str] = []
    
    # 🌾 FARMER ADVISORY (Kisan)
    if persona == PersonaType.FARMER:
        if weather.precipitation_probability > 50 or weather.precipitation > 2.0:
            if lang == LanguageType.HINDI:
                advisories.append("🌧️ सिंचाई स्थगित करें: बारिश की संभावना 50%+ है, जिससे फसल में जलभराव हो सकता है।")
                advisories.append("🚫 कीटनाशक/उर्वरक का छिड़काव न करें: बारिश के कारण दवाई बह जाएगी।")
            elif lang == LanguageType.HINGLISH:
                advisories.append("🌧️ Irrigation Delay Karein: Baarish ke chances 50%+ hain, zameen me pehle se nami rahegi.")
                advisories.append("🚫 Spraying Mat Karein: Fertilizer aur pesticide spray baarish me wash out ho jayega.")
            else:
                advisories.append("🌧️ Postpone Irrigation: High rain probability (>50%); avoid waterlogging.")
                advisories.append("🚫 Halt Pesticide Spraying: Rainfall will cause chemical wash-off and financial loss.")
        else:
            if lang == LanguageType.HINDI:
                advisories.append("💧 सिंचाई के लिए उपयुक्त समय: आगामी 24 घंटों में तेज बारिश की संभावना कम है।")
            elif lang == LanguageType.HINGLISH:
                advisories.append("💧 Safe for Irrigation: Agle 24 hours me bhaari baarish ke chances kam hain.")
            else:
                advisories.append("💧 Favorable Window: Next 24 hours are suitable for light furrow irrigation.")

        if weather.wind_speed > 18.0:
            if lang == LanguageType.HINDI:
                advisories.append(f"💨 तेज हवा चेतावनी ({weather.wind_speed} km/h): लंबी फसलों में लॉजिंग (गिरने) का खतरा।")
            elif lang == LanguageType.HINGLISH:
                advisories.append(f"💨 Tezz Hawa Warning ({weather.wind_speed} km/h): Spraying me drift hoga, ped aur sheds ko protect karein.")
            else:
                advisories.append(f"💨 High Wind Alert ({weather.wind_speed} km/h): Unfavorable for high-pressure foliar spraying.")

    # ✈️ TRAVELER ADVISORY (Yatri)
    elif persona == PersonaType.TRAVELER:
        if weather.precipitation_probability > 40:
            if lang == LanguageType.HINDI:
                advisories.append("🚗 सड़क फिसलन चेतावनी: गीली सड़कों पर ब्रेक दूरी बढ़ सकती है, सुरक्षित गति रखें।")
            elif lang == LanguageType.HINGLISH:
                advisories.append("🚗 Road Hydroplaning Risk: Geeli sadak par braking distance badhegi, 60 km/h se neeche drive karein.")
            else:
                advisories.append("🚗 Hydroplaning Hazard: Wet asphalt reduces tire grip; maintain a 3-second braking buffer.")

        if weather.weather_code in [45, 48]:
            if lang == LanguageType.HINDI:
                advisories.append("🌫️ घना कोहरा: फॉग लैंप का प्रयोग करें और हेडलाइट लो-बीम पर रखें।")
            elif lang == LanguageType.HINGLISH:
                advisories.append("🌫️ Dense Fog: Visibility kam hai, high-beam ke bajay low-beam fog lights on rakhein.")
            else:
                advisories.append("🌫️ Reduced Visibility: Dense fog conditions; use amber fog lamps and low beams.")

        if not advisories:
            if lang == LanguageType.HINDI:
                advisories.append("✅ यात्रा के लिए अनुकूल मौसम: सड़कें साफ और दृश्यता अच्छी रहेगी।")
            elif lang == LanguageType.HINGLISH:
                advisories.append("✅ Good Travel Conditions: Driving visibility clear hai aur highway safar smooth rahega.")
            else:
                advisories.append("✅ Clear Travel Conditions: Optimal road visibility and stable flight operations expected.")

    # 🏙️ CITIZEN ADVISORY (Nagrik)
    elif persona == PersonaType.CITIZEN:
        if weather.precipitation_probability > 40 or weather.precipitation > 1.0:
            if lang == LanguageType.HINDI:
                advisories.append("☂️ छाता साथ रखें: आज बारिश या बूंदाबांदी की पूरी संभावना है।")
            elif lang == LanguageType.HINGLISH:
                advisories.append("☂️ Umbrella / Raincoat Saath Rakhein: Baarish ke acche chances hain.")
            else:
                advisories.append("☂️ Carry an Umbrella: Rain showers are anticipated during commuting hours.")

        if weather.uv_index >= 7.0:
            if lang == LanguageType.HINDI:
                advisories.append(f"☀️ उच्च यूवी सूचकांक ({weather.uv_index}): दोपहर में धूप का चश्मा और सनस्क्रीन लगाएं।")
            elif lang == LanguageType.HINGLISH:
                advisories.append(f"☀️ High UV Index ({weather.uv_index}): Dopahar me direct dhoop se bachein aur paani peete rahein.")
            else:
                advisories.append(f"☀️ High UV Index ({weather.uv_index}): Seek shade between 12-3 PM and wear UV-rated sunglasses.")

        if weather.temperature >= 38.0:
            if lang == LanguageType.HINDI:
                advisories.append(f"🔥 तेज गर्मी ({weather.temperature}°C): निर्जलीकरण से बचने के लिए भरपूर पानी पिएं।")
            elif lang == LanguageType.HINGLISH:
                advisories.append(f"🔥 Garmi Alert ({weather.temperature}°C): Dehydration se bachne ke liye glucose/nimbu paani carry karein.")
            else:
                advisories.append(f"🔥 Elevated Thermal Index ({weather.temperature}°C): Stay well hydrated to prevent heat fatigue.")

    # 🚨 DISASTER OFFICER ADVISORY
    elif persona == PersonaType.DISASTER_OFFICER:
        if weather.precipitation > 20 or weather.weather_code in [65, 82, 95, 96, 99]:
            advisories.append("🚨 Rapid Inundation Monitor: Low-lying culverts and storm drains require field supervisor deployment.")
            advisories.append("📞 Inter-Agency Alert: Keep State SDRF & Emergency Operations Centre on stand-by alert level 2.")
        else:
            advisories.append("🟢 Normal Preparedness: Weather indices remain below threshold level Yellow. Routine logging.")

    return advisories
