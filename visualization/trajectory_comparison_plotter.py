import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import contextily as cx

def plot_trajectory_comparison(csv_path: str, comparison_data: list, output_filename: str, city: str = "Porto"):
    df = pd.read_csv(csv_path)
    geometry = [Point(xy) for xy in zip(df.Lon, df.Lat)]
    gdf_trajectory = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry).to_crs(epsg=3857)

    llm_points = []
    api_points = []
    lines = []
    names = []

    for item in comparison_data:
        p_llm = Point(item["llm_lon"], item["llm_lat"])
        p_api = Point(item["api_lon"], item["api_lat"])
        llm_points.append(p_llm)
        api_points.append(p_api)
        lines.append(LineString([p_llm, p_api]))
        names.append(item["name"])

    fig, ax = plt.subplots(figsize=(14, 12), dpi=150)
    
    # Trajectory points
    gdf_trajectory.plot(ax=ax, color='red', markersize=10, alpha=0.5, label='Actual Trajectory', zorder=2)
    
    if comparison_data:
        gdf_llm = gpd.GeoDataFrame({"POI": names}, geometry=llm_points, crs="EPSG:4326").to_crs(epsg=3857)
        gdf_api = gpd.GeoDataFrame({"POI": names}, geometry=api_points, crs="EPSG:4326").to_crs(epsg=3857)
        gdf_lines = gpd.GeoDataFrame(geometry=lines, crs="EPSG:4326").to_crs(epsg=3857)

        # Lines connecting LLM and API
        gdf_lines.plot(ax=ax, color='gray', linestyle='--', linewidth=1.5, zorder=4)

        # LLM points (Blue)
        gdf_llm.plot(ax=ax, marker='o', color='blue', edgecolor='white', markersize=120, label='LLM', zorder=5)

        # API points (Gold Stars)
        gdf_api.plot(ax=ax, marker='*', color='gold', edgecolor='black', markersize=250, label='API (Google)', zorder=6)

        for idx, row in gdf_api.iterrows():
            ax.text(row.geometry.x + 80, row.geometry.y + 80, str(idx + 1), 
                    fontsize=11, weight='bold', color='black', 
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1),
                    zorder=7)
            
        legend_labels = [f"{i+1}: {name}" for i, name in enumerate(names)]
        legend_text = "\n".join(legend_labels)
        props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
        ax.text(1.02, 0.98, legend_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)

    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)
    
    ax.set_axis_off()
    ax.legend(loc="upper left", fontsize=12)
    
    plt.title(f"Trajectory LLM vs API | {city}", fontsize=16, weight="bold")
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight', dpi=200)
    plt.close()
    print(f" -> Comparison map saved to: {output_filename}")
