import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as cx

def plot_pois(pois_data: list, output_filename: str, city: str = "Porto"):
    if not pois_data:
        print("No POIs to plot.")
        return

    # Δημιουργία GeoDataFrame
    points = []
    names = []
    for item in pois_data:
        points.append(Point(item["lon"], item["lat"]))
        names.append(item["name"])

    gdf = gpd.GeoDataFrame({"POI": names}, geometry=points, crs="EPSG:4326")
    
    # Μετατροπή σε EPSG:3857 για συμβατότητα με basemaps
    gdf = gdf.to_crs(epsg=3857)

    # Δημιουργία Plot
    fig, ax = plt.subplots(figsize=(14, 12), dpi=150)
    
    # Σχεδιασμός των σημείων (κόκκινες τελείες)
    gdf.plot(ax=ax, marker='o', color='red', edgecolor='black', markersize=150, zorder=5)

    # Προσθήκη αριθμών δίπλα στα σημεία
    for idx, row in gdf.iterrows():
        # Μικρό offset για να μην πέφτει ο αριθμός πάνω στην τελεία
        ax.text(row.geometry.x + 80, row.geometry.y + 80, str(idx + 1), 
                fontsize=11, weight='bold', color='black', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1),
                zorder=6)

    #Auto-zoom
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    x_margin = (bounds[2] - bounds[0]) * 0.2 + 500 # 20% περιθώριο + τουλάχιστον 500μ
    y_margin = (bounds[3] - bounds[1]) * 0.2 + 500
    
    ax.set_xlim(bounds[0] - x_margin, bounds[2] + x_margin)
    ax.set_ylim(bounds[1] - y_margin, bounds[3] + y_margin)

    # Προσθήκη Basemap (OpenStreetMap)
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)

    ax.set_axis_off()

    # Δημιουργία Legend στα δεξιά
    legend_labels = [f"{i+1}: {name}" for i, name in enumerate(names)]
    legend_text = "\n".join(legend_labels)
    
    # Τοποθέτηση του text box για το legend
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
    ax.text(1.02, 0.98, legend_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props, family='sans-serif')

    plt.title(f"Story POIs | {city}", fontsize=16, weight="bold", pad=20)
    
    # Αποθήκευση
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight', dpi=200)
    plt.close()
    print(f" -> Map with POIs saved to: {output_filename}")

if __name__ == "__main__":
    # Test with dummy data
    test_pois = [
        {"name": "Station #1", "lon": -8.61099, "lat": 41.14557},
        {"name": "Tower #2", "lon": -8.6142, "lat": 41.1456},
        {"name": "Road #3 ", "lon": -8.6139, "lat": 41.1459}
    ]
    plot_pois(test_pois, "test_poi_map.png")
