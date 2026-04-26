import os
import json
from dotenv import load_dotenv
import config
from visualization.comparison_plotter import plot_heatmap_comparison

from geocoders.google_geocoder import geocode_pois

def main():
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    # Choose the file to test.
    city = "Attica"
    country = "Greece"
    pois_file = os.path.join(config.STORY_OUTPUT, "athens_fake_pois_athens_unbiased.json")
    
    if not os.path.exists(pois_file):
        print(f"Error: {pois_file} not found. Run test_07 first.")
        return
        
    with open(pois_file, "r", encoding="utf-8") as f:
        pois = json.load(f)

    if not pois:
        print("No POIs found for geocoding.")
        return

    print(f"=== Checking {len(pois)} POIs with Google Places Geocoder ===")
    result_dict = geocode_pois(pois, city, country, api_key=google_api_key)
    comparison_data = result_dict["results"]
    
    if comparison_data:
        comparison_file = os.path.join(config.STORY_OUTPUT, "athens_google_comparison.json")
        with open(comparison_file, "w", encoding="utf-8") as f:
            json.dump(comparison_data, f, ensure_ascii=False, indent=4)
        print(f"\nComparison data saved to: {comparison_file}")
        
        plot_file = os.path.join(config.STORY_OUTPUT, "athens_google_comparison_map.png")
        plot_heatmap_comparison(comparison_data, plot_file, city=city)
    else:
        print("No comparison data generated.")

if __name__ == "__main__":
    main()
