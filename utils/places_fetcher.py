import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString

def get_nearby_pois(lat: float, lon: float, api_key: str, radius: int = 150, types: str = None, max_results: int = 2) -> list:
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&key={api_key}"
    
    if types:
        url += f"&type={types}"
        
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") == "OK":
            pois = []
            for item in data.get("results", [])[:max_results]:
                pois.append({
                    "name": item['name'],
                    "types": item.get('types', [])[:2],
                    "lat": item['geometry']['location']['lat'],
                    "lon": item['geometry']['location']['lng']
                })
            return pois
        return []
    except Exception as e:
        print(f"[DEBUG] Nearby Search error: {e}")
        return []

def sample_trajectory_points(csv_path: str, interval_meters: float = 500.0) -> list:
    df = pd.read_csv(csv_path)
    if len(df) < 2:
        return []
        
    # Project to EPSG:32629 (UTM 29N)
    points = [Point(lon, lat) for lon, lat in zip(df.Lon, df.Lat)]
    gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326").to_crs("EPSG:32629")
    line = LineString(gdf.geometry.tolist())
    
    sampled_points_lat_lon = []
    
    # Generate distances: 0, 500, 1000... up to line length
    distances = []
    d = 0.0
    while d < line.length:
        distances.append(d)
        d += interval_meters
        
    if line.length not in distances:
        distances.append(line.length)
        
    # Interpolate points along the line
    for d in distances:
        pt_utm = line.interpolate(d)
        # Convert back to EPSG:4326
        pt_wgs84 = gpd.GeoSeries([pt_utm], crs="EPSG:32629").to_crs("EPSG:4326").iloc[0]
        sampled_points_lat_lon.append((pt_wgs84.y, pt_wgs84.x))
        
    return sampled_points_lat_lon
