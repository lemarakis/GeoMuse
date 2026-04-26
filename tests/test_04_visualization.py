import os
import json
import config
from visualization.poi_plotter import plot_pois

def main():
    pois_file = os.path.join(config.STORY_OUTPUT, "porto_extracted_pois.json")
    
    if not os.path.exists(pois_file):
        print(f"Error: {pois_file} not found. Please run test_03 first.")
        return

    with open(pois_file, "r", encoding="utf-8") as f:
        pois = json.load(f)

    print(f"Loaded {len(pois)} POIs from JSON.")

    output_map = os.path.join(config.STORY_OUTPUT, "porto_poi_map.png")
    
    print("=== STEP 3: POI Visualization ===")
    plot_pois(pois, output_map, city="Porto")
    
    print(f"\nVisualization complete! Check the result at: {output_map}")

if __name__ == "__main__":
    main()
