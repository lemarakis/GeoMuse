import os
import json
from dotenv import load_dotenv

import config
from geocoders.google_geocoder import geocode_pois
from visualization.trajectory_comparison_plotter import plot_trajectory_comparison

def main():
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    city = "Porto"
    country = "Portugal"
    
    # trajectory POIs
    pois_file = os.path.join(config.STORY_OUTPUT, "porto_trajectory_pois.json")
    trajectory_csv = os.path.join(config.BASE_DIR, "sstd2025", "trajectory.csv")
    
    if not os.path.exists(pois_file):
        print(f"Error: {pois_file} not found. Run test_05 first.")
        return
        
    if not os.path.exists(trajectory_csv):
        print(f"Error: {trajectory_csv} not found.")
        return

    with open(pois_file, "r", encoding="utf-8") as f:
        pois = json.load(f)

    if not pois:
        print("No POIs found for geocoding.")
        return

    print(f"=== Checking {len(pois)} POIs from Trajectory Story with Google Places Geocoder ===")
    result_dict = geocode_pois(pois, city, country, api_key=google_api_key)
    comparison_data = result_dict["results"]
    
    if comparison_data:
        comparison_file = os.path.join(config.STORY_OUTPUT, "porto_trajectory_google_comparison.json")
        with open(comparison_file, "w", encoding="utf-8") as f:
            json.dump(comparison_data, f, ensure_ascii=False, indent=4)
        print(f"\nComparison data saved to: {comparison_file}")
        
        plot_file = os.path.join(config.STORY_OUTPUT, "porto_trajectory_google_comparison_map.png")
        plot_trajectory_comparison(trajectory_csv, comparison_data, plot_file, city=city)

if __name__ == "__main__":
    main()
