import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
import matplotlib.pyplot as plt
import contextily as cx

def plot_trajectory_deviation(csv_path: str, deviation_data: list, output_filename: str, city: str = "Porto", use_llm_coords: bool = False):
    # Load trajectory
    df = pd.read_csv(csv_path)
    geometry = [Point(xy) for xy in zip(df.Lon, df.Lat)]
    gdf_trajectory = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry).to_crs(epsg=3857)
    
    # Create a single LineString in projected coordinates to find the nearest point
    traj_line_3857 = LineString(gdf_trajectory.geometry.tolist())

    api_points = []
    deviation_lines = []
    names = []
    distances = []

    for item in deviation_data:
        if use_llm_coords:
            target_lon = float(item.get("llm_lon"))
            target_lat = float(item.get("llm_lat"))
        else:
            target_lon = item.get("api_lon")
            target_lat = item.get("api_lat")
            
        p_api = Point(target_lon, target_lat)
        names.append(item["name"])
        distances.append(item.get("distance_to_trajectory_meters", 0))
        
        # Project API point to 3857
        p_api_3857 = gpd.GeoSeries([p_api], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
        api_points.append(p_api_3857)
        
        # Find nearest point on the trajectory line
        closest_pt_on_line, _ = nearest_points(traj_line_3857, p_api_3857)
        
        # Create a line connecting the POI to the closest point on the route
        deviation_lines.append(LineString([p_api_3857, closest_pt_on_line]))

    fig, ax = plt.subplots(figsize=(14, 12), dpi=150)
    
    # Plot Trajectory (Red)
    gdf_trajectory.plot(ax=ax, color='red', markersize=10, alpha=0.5, label='Actual Trajectory', zorder=2)
    
    if deviation_data:
        gdf_api = gpd.GeoDataFrame({"POI": names}, geometry=api_points, crs="EPSG:3857")
        gdf_lines = gpd.GeoDataFrame(geometry=deviation_lines, crs="EPSG:3857")

        # Plot Deviation Lines (Gray Dashed)
        gdf_lines.plot(ax=ax, color='gray', linestyle='--', linewidth=1.5, zorder=4)

        # Plot API points (Gold Stars)
        gdf_api.plot(ax=ax, marker='*', color='gold', edgecolor='black', markersize=250, label='Actual POI Location', zorder=6)

        # Add labels with distance
        for idx, row in gdf_api.iterrows():
            dist = distances[idx]
            dist_text = f"{dist/1000:.1f}km" if dist > 1000 else f"{int(dist)}m"
            label = f"{idx + 1} ({dist_text})"
            
            ax.text(row.geometry.x + 80, row.geometry.y + 80, label, 
                    fontsize=10, weight='bold', color='black', 
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1),
                    zorder=7)
            
        legend_labels = [f"{i+1}: {name}" for i, name in enumerate(names)]
        legend_text = "\n".join(legend_labels)
        props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
        ax.text(1.02, 0.98, legend_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)

    # Add Basemap
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)
    
    ax.set_axis_off()
    ax.legend(loc="upper left", fontsize=12)
    
    plt.title(f"Trajectory Deviation | {city}", fontsize=16, weight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight', dpi=200)
    plt.close()
    print(f" -> Deviation map saved to: {output_filename}")
