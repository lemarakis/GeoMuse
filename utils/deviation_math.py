import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString

def calculate_average_deviation(trajectory_csv: str, comparison_pois: list, print_results: bool = False, use_llm_coords: bool = False) -> float:
    """
    Calculates the average distance (in meters) from a list of POIs to a trajectory LineString.
    Returns 0.0 if no POIs are provided or no valid coordinates exist.
    Mutates the comparison_pois list to add 'distance_to_trajectory_meters'.
    """
    if not comparison_pois:
        return 0.0
        
    df = pd.read_csv(trajectory_csv)
    trajectory_line = LineString([Point(lon, lat) for lon, lat in zip(df.Lon, df.Lat)])
    
    # Project to EPSG:32629 (UTM 29N) for Portugal metric accuracy
    gdf_traj = gpd.GeoDataFrame(geometry=[trajectory_line], crs="EPSG:4326").to_crs("EPSG:32629")
    metric_line = gdf_traj.geometry.iloc[0]

    total_deviation = 0.0
    valid_points_count = 0
    
    for i, item in enumerate(comparison_pois):
        if use_llm_coords:
            target_lon = float(item.get("llm_lon"))
            target_lat = float(item.get("llm_lat"))
        else:
            target_lon = item.get("api_lon")
            target_lat = item.get("api_lat")
            
        if target_lon is None or target_lat is None:
            continue
            
        poi_point = Point(target_lon, target_lat)
        gdf_poi = gpd.GeoDataFrame(geometry=[poi_point], crs="EPSG:4326").to_crs("EPSG:32629")
        metric_point = gdf_poi.geometry.iloc[0]
        
        distance_meters = metric_point.distance(metric_line)
        total_deviation += distance_meters
        valid_points_count += 1
        
        item["distance_to_trajectory_meters"] = round(distance_meters, 1)
        
        if print_results:
            safe_name = item.get("name", "").encode('ascii', 'ignore').decode('ascii')
            print(f"[{i+1}/{len(comparison_pois)}] {safe_name} is {distance_meters:.1f} meters away from the route.")
        
    if valid_points_count == 0:
        return 0.0
        
    avg = total_deviation / valid_points_count
    
    if print_results:
        print(f"\nAverage POI Deviation from Route: {avg:.1f} meters")
        
    return avg
