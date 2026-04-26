import time
from geopy.geocoders import ArcGIS
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.distance import geodesic

def geocode_pois(pois: list, city: str, country: str, api_key: str = None) -> dict:
    geolocator = ArcGIS()
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
            
            if location:
                dist_m = geodesic((llm_lat, llm_lon), (location.latitude, location.longitude)).meters
                results.append({
                    "name": name,
                    "llm_lon": llm_lon,
                    "llm_lat": llm_lat,
                    "api_lon": location.longitude,
                    "api_lat": location.latitude,
                    "diff_distance_meters": round(dist_m, 1)
                })
                hits += 1
            else:
                pass
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            pass
            
    return {
        "name": "ArcGIS",
        "hits": hits,
        "total": len(pois),
        "results": results
    }
