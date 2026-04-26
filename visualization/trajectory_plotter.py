import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as cx

def plot_trajectory_with_pois(csv_path: str, pois_data: list, output_filename: str, city: str = "Porto"):

    # Load trajectory from CSV
    df = pd.read_csv(csv_path)

    # Δημιουργία GeoDataFrame για τα σημεία της διαδρομής
    geometry = [Point(xy) for xy in zip(df.Lon, df.Lat)]
    gdf_trajectory = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
    gdf_trajectory = gdf_trajectory.to_crs(epsg=3857)

    # Load POIs
    llm_points = []
    names = []
    for item in pois_data:
        llm_points.append(Point(item["lon"], item["lat"]))
        names.append(item["name"])
    
    gdf_pois = gpd.GeoDataFrame({"POI": names}, geometry=llm_points, crs="EPSG:4326")
    gdf_pois = gdf_pois.to_crs(epsg=3857)

    # Plotting
    fig, ax = plt.subplots(figsize=(14, 12), dpi=150)
    
    # Plot trajectory (Κόκκινες Κουκίδες)
    gdf_trajectory.plot(ax=ax, color='red', markersize=10, alpha=0.5, label='Actual Trajectory Points', zorder=2)
    
    # Plot POIs (Μπλε Αστέρια)
    gdf_pois.plot(ax=ax, marker='*', color='blue', edgecolor='white', markersize=250, label='LLM POIs', zorder=5)

    # Προσθήκη αριθμών στα POIs
    for idx, row in gdf_pois.iterrows():
        ax.text(row.geometry.x + 80, row.geometry.y + 80, str(idx + 1), 
                fontsize=11, weight='bold', color='black', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1),
                zorder=6)

    # Προσθήκη Basemap
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)

    ax.set_axis_off()

    # Legend για τα POIs
    legend_labels = [f"{i+1}: {name}" for i, name in enumerate(names)]
    legend_text = "\n".join(legend_labels)
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
    ax.text(1.02, 0.98, legend_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    plt.title(f"Trajectory | {city}", fontsize=16, weight="bold")
    plt.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight', dpi=200)
    plt.close()
    print(f" -> Trajectory map saved to: {output_filename}")

if __name__ == "__main__":
    pass
