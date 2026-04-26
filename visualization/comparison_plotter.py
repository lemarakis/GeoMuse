import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString, Point
import contextily as cx

def plot_heatmap_comparison(comparison_data: list, output_filename: str, city: str = "Porto"):
    if not comparison_data:
        print("No comparison data to plot.")
        return

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
    
    gdf_llm = gpd.GeoDataFrame({"POI": names}, geometry=llm_points, crs="EPSG:4326").to_crs(epsg=3857)
    gdf_api = gpd.GeoDataFrame({"POI": names}, geometry=api_points, crs="EPSG:4326").to_crs(epsg=3857)
    gdf_lines = gpd.GeoDataFrame(geometry=lines, crs="EPSG:4326").to_crs(epsg=3857)

    # Γραμμές σφάλματος
    gdf_lines.plot(ax=ax, color='gray', linestyle='--', linewidth=1.5, zorder=4)

    # LLM σημεία (Μπλε τελείες)
    gdf_llm.plot(ax=ax, marker='o', color='blue', edgecolor='white', markersize=120, label='LLM', zorder=5)

    # API πραγματικά σημεία (Χρυσά Αστέρια)
    gdf_api.plot(ax=ax, marker='*', color='gold', edgecolor='black', markersize=250, label='API (Google)', zorder=6)

    # Προσθήκη αριθμών δίπλα στα σημεία του API
    for idx, row in gdf_api.iterrows():
        ax.text(row.geometry.x + 80, row.geometry.y + 80, str(idx + 1), 
                fontsize=11, weight='bold', color='black', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1),
                zorder=7)

    # Auto-zoom
    all_points_gdf = gpd.GeoDataFrame(geometry=llm_points + api_points, crs="EPSG:4326").to_crs(epsg=3857)
    bounds = all_points_gdf.total_bounds
    x_margin = (bounds[2] - bounds[0]) * 0.2 + 500
    y_margin = (bounds[3] - bounds[1]) * 0.2 + 500
    
    ax.set_xlim(bounds[0] - x_margin, bounds[2] + x_margin)
    ax.set_ylim(bounds[1] - y_margin, bounds[3] + y_margin)

    # Προσθήκη Basemap (OpenStreetMap)
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)

    ax.set_axis_off()

    # Δημιουργία Legend στα δεξιά
    legend_labels = [f"{i+1}: {name}" for i, name in enumerate(names)]
    legend_text = "\n".join(legend_labels)
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
    ax.text(1.02, 0.98, legend_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props, family='sans-serif')
            
    ax.legend(loc="upper right", fontsize=12)

    plt.title(f"LLM vs Google Places | {city}", fontsize=16, weight="bold", pad=20)
    
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight', dpi=200)
    plt.close()
    print(f" -> Comparison map saved to: {output_filename}")
