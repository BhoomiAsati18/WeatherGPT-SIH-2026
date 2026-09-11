from typing import Optional, List
from ..models.schemas import AlertItem, AlertSeverity, WeatherCardData

# Active Disaster Alert Registry (Simulating NDMA SACHET / IMD CAP Bulletins)
REGIONAL_CAP_ALERTS = [
    {
        "district": "mumbai",
        "severity": AlertSeverity.WARNING,
        "category": "Heavy Rainfall & High Tide",
        "headline": "Orange Alert: Heavy to Very Heavy Rain with High Tide Warning",
        "description": "IMD Mumbai issues Orange warning for coastal areas. High tide of 4.2m expected at 14:30 hrs.",
        "instructions": [
            "Avoid visiting seaside promenades and beaches.",
            "Expect waterlogging in low-lying railway underpasses.",
            "Keep emergency contact numbers handy (Disaster Control: 1916)."
        ],
        "source": "IMD Regional Met Centre & NDMA SACHET",
        "color_hex": "#ea580c"
    },
    {
        "district": "indore",
        "severity": AlertSeverity.WATCH,
        "category": "Isolated Thunderstorm",
        "headline": "Yellow Watch: Thunderstorm accompanied with Gusty Winds (30-40 km/h)",
        "description": "Convective clouds active over Malwa plateau. Brief spells of rain with lightning likely in evening hours.",
        "instructions": [
            "Do not take shelter under solitary trees during lightning.",
            "Secure loose metal sheets and outdoor farm covers."
        ],
        "source": "IMD Bhopal Met Centre",
        "color_hex": "#eab308"
    },
    {
        "district": "delhi",
        "severity": AlertSeverity.WATCH,
        "category": "Thermal Stress & Air Quality",
        "headline": "Moderate Heat Stress & Dust Haze Warning",
        "description": "Daytime peak temperatures reaching 38-41°C with dry westerly winds.",
        "instructions": [
            "Stay hydrated and avoid direct sun exposure between 12:00 PM and 3:30 PM.",
            "Wear light cotton clothing."
        ],
        "source": "IMD New Delhi",
        "color_hex": "#eab308"
    }
]

def evaluate_disaster_alerts(weather: WeatherCardData, location_query: str) -> Optional[AlertItem]:
    """
    Evaluates verified meteorological conditions and regional alerts to produce
    grounded disaster warnings (IMD/NDMA standard compliant).
    """
    loc_clean = location_query.lower()

    # 1. Check active CAP / NDMA Registry
    for alert_def in REGIONAL_CAP_ALERTS:
        if alert_def["district"] in loc_clean or alert_def["district"] in weather.location.lower():
            return AlertItem(
                severity=alert_def["severity"],
                category=alert_def["category"],
                headline=alert_def["headline"],
                description=alert_def["description"],
                instructions=alert_def["instructions"],
                source=alert_def["source"],
                color_hex=alert_def["color_hex"]
            )

    # 2. Rule-based Meteorological Thresholds (Grounded Evaluation)
    # Severe Rain
    if weather.precipitation > 25.0 or (weather.precipitation_probability > 80 and weather.weather_code in [65, 82, 95, 96, 99]):
        return AlertItem(
            severity=AlertSeverity.WARNING,
            category="Heavy Precipitation",
            headline="⚠️ Orange Alert: Severe Rain & Thunderstorm Expected",
            description=f"Significant rainfall ({weather.precipitation}mm) or violent downpour detected with probability {weather.precipitation_probability}%.",
            instructions=[
                "Farmers: Pause all pesticide spraying and clear drainage trenches.",
                "Commuters: Avoid waterlogged low-lying roads and subway routes.",
                "Ensure electronic devices are fully charged in case of local power outage."
            ],
            source="Automated Weather Alert Engine (IMD Criteria)",
            color_hex="#ea580c"
        )

    # Extreme Wind / Storm
    if weather.wind_speed > 45.0:
        return AlertItem(
            severity=AlertSeverity.WARNING,
            category="High Winds / Gale",
            headline="💨 Wind Hazard Warning: Gusts exceeding 45 km/h",
            description=f"Strong wind gusts recorded at {weather.wind_speed} km/h. Risk of fallen branches and damaged farm shelters.",
            instructions=[
                "Secure tin sheds, solar panels, and outdoor equipment.",
                "Two-wheelers and high-sided vehicles should drive with extreme caution."
            ],
            source="IMD Gust Risk Index",
            color_hex="#ea580c"
        )

    # Extreme Heatwave
    if weather.temperature >= 42.0:
        return AlertItem(
            severity=AlertSeverity.SEVERE,
            category="Extreme Heatwave",
            headline="🚨 Red Alert: Severe Heatwave Conditions",
            description=f"Dangerous ambient temperature of {weather.temperature}°C (Apparent: {weather.apparent_temperature}°C). Extreme risk of heatstroke.",
            instructions=[
                "Avoid going outdoors between 11:30 AM and 4:00 PM.",
                "Drink oral rehydration salts (ORS), lassi, or lemon water frequently.",
                "Provide shaded water points for livestock and pets."
            ],
            source="NDMA Heatwave Action Plan",
            color_hex="#dc2626"
        )

    # Mild Warning / Watch
    if weather.weather_code in [95, 96]:
        return AlertItem(
            severity=AlertSeverity.WATCH,
            category="Thunderstorm & Lightning",
            headline="⚡ Yellow Watch: Thunderstorm Activity",
            description="Lightning bursts and convective cloud formation observed.",
            instructions=[
                "Unplug sensitive electrical appliances.",
                "Do not stand under open umbrellas in wide fields."
            ],
            source="Damini Lightning Risk Network",
            color_hex="#eab308"
        )

    return None
