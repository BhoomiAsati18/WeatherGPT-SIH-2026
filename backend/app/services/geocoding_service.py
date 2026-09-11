import httpx
from typing import Optional, Dict, Any

INDIAN_CITY_FALLBACKS = {
    "indore": {"name": "Indore", "latitude": 22.7196, "longitude": 75.8577, "admin1": "Madhya Pradesh", "country": "India"},
    "bhopal": {"name": "Bhopal", "latitude": 23.2599, "longitude": 77.4126, "admin1": "Madhya Pradesh", "country": "India"},
    "delhi": {"name": "Delhi", "latitude": 28.6139, "longitude": 77.2090, "admin1": "Delhi", "country": "India"},
    "new delhi": {"name": "New Delhi", "latitude": 28.6139, "longitude": 77.2090, "admin1": "Delhi", "country": "India"},
    "mumbai": {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777, "admin1": "Maharashtra", "country": "India"},
    "pune": {"name": "Pune", "latitude": 18.5204, "longitude": 73.8567, "admin1": "Maharashtra", "country": "India"},
    "jaipur": {"name": "Jaipur", "latitude": 26.9124, "longitude": 75.7873, "admin1": "Rajasthan", "country": "India"},
    "lucknow": {"name": "Lucknow", "latitude": 26.8467, "longitude": 80.9462, "admin1": "Uttar Pradesh", "country": "India"},
    "patna": {"name": "Patna", "latitude": 25.5941, "longitude": 85.1376, "admin1": "Bihar", "country": "India"},
    "kolkata": {"name": "Kolkata", "latitude": 22.5726, "longitude": 88.3639, "admin1": "West Bengal", "country": "India"},
    "bengaluru": {"name": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946, "admin1": "Karnataka", "country": "India"},
    "bangalore": {"name": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946, "admin1": "Karnataka", "country": "India"},
    "chennai": {"name": "Chennai", "latitude": 13.0827, "longitude": 80.2707, "admin1": "Tamil Nadu", "country": "India"},
    "hyderabad": {"name": "Hyderabad", "latitude": 17.3850, "longitude": 78.4867, "admin1": "Telangana", "country": "India"},
    "ahmedabad": {"name": "Ahmedabad", "latitude": 23.0225, "longitude": 72.5714, "admin1": "Gujarat", "country": "India"},
    "chandigarh": {"name": "Chandigarh", "latitude": 30.7333, "longitude": 76.7794, "admin1": "Punjab", "country": "India"},
    "varanasi": {"name": "Varanasi", "latitude": 25.3176, "longitude": 82.9739, "admin1": "Uttar Pradesh", "country": "India"},
    "kanpur": {"name": "Kanpur", "latitude": 26.4499, "longitude": 80.3319, "admin1": "Uttar Pradesh", "country": "India"},
    "nagpur": {"name": "Nagpur", "latitude": 21.1458, "longitude": 79.0882, "admin1": "Maharashtra", "country": "India"},
    "surat": {"name": "Surat", "latitude": 21.1702, "longitude": 72.8311, "admin1": "Gujarat", "country": "India"},
    "visakhapatnam": {"name": "Visakhapatnam", "latitude": 17.6868, "longitude": 83.2185, "admin1": "Andhra Pradesh", "country": "India"},
    "shimla": {"name": "Shimla", "latitude": 31.1048, "longitude": 77.1734, "admin1": "Himachal Pradesh", "country": "India"},
    "dehradun": {"name": "Dehradun", "latitude": 30.3165, "longitude": 78.0322, "admin1": "Uttarakhand", "country": "India"},
    "srinagar": {"name": "Srinagar", "latitude": 34.0837, "longitude": 74.7973, "admin1": "Jammu and Kashmir", "country": "India"},
}

GEOCODING_CACHE: Dict[str, Dict[str, Any]] = {}

async def resolve_location(query_or_city: str) -> Optional[Dict[str, Any]]:
    """Resolves location name to {name, latitude, longitude, admin1, country}."""
    clean_name = query_or_city.strip().lower()
    
    # Check memory cache
    if clean_name in GEOCODING_CACHE:
        return GEOCODING_CACHE[clean_name]
        
    # Check offline Indian fallback database
    for key, val in INDIAN_CITY_FALLBACKS.items():
        if key in clean_name or clean_name in key:
            GEOCODING_CACHE[clean_name] = val
            return val

    # Online Open-Meteo Geocoding API
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_name}&count=1&language=en&format=json"
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results")
                if results and len(results) > 0:
                    top = results[0]
                    resolved = {
                        "name": top.get("name", query_or_city.title()),
                        "latitude": float(top.get("latitude")),
                        "longitude": float(top.get("longitude")),
                        "admin1": top.get("admin1", ""),
                        "country": top.get("country", "India")
                    }
                    GEOCODING_CACHE[clean_name] = resolved
                    return resolved
    except Exception as e:
        print(f"Geocoding API error for {query_or_city}: {e}")

    # Fallback to Delhi if unknown
    return INDIAN_CITY_FALLBACKS["delhi"]
