import time
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.distance import geodesic

def geocode_pois(pois: list, city: str, country: str, api_key: str = None) -> dict:
    if not api_key:
        print("Google API Key missing.")
        return {"name": "Google", "hits": 0, "total": len(pois), "results": []}

    geolocator = GoogleV3(api_key=api_key)
    results = []
    hits = 0

    for i, item in enumerate(pois):
        name = item["name"]
        llm_lon = item.get("lon")
        llm_lat = item.get("lat")
        
        if llm_lon is None or llm_lat is None:
            continue
            
        query = f"{name}, {city}, {country}"
        
        try:
            time.sleep(1.0)
            location = geolocator.geocode(query)
            
            safe_name = name.encode('ascii', 'ignore').decode('ascii')
            
            if location:
                try:
                    dist_m = geodesic((float(llm_lat), float(llm_lon)), (location.latitude, location.longitude)).meters
                    results.append({
                        "name": name,
                        "llm_lon": llm_lon,
                        "llm_lat": llm_lat,
                        "api_lon": location.longitude,
                        "api_lat": location.latitude,
                        "diff_distance_meters": round(dist_m, 1)
                    })
                    hits += 1
                except (ValueError, TypeError) as ve:
                    pass
            else:
                pass
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            pass
            
    return {
        "name": "Google",
        "hits": hits,
        "total": len(pois),
        "results": results
    }
