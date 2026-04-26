import os
import json
from dotenv import load_dotenv

import config
from geocoders import google_geocoder
from geocoders import nominatim_geocoder
from geocoders import arcgis_geocoder

def evaluate_geocoders(pois: list, google_api_key: str, city: str, country: str):
    print(f"=== Evaluator: Testing {len(pois)} POIs across 3 Geocoders ===")
    
    geocoders = [
        google_geocoder.geocode_pois,
        nominatim_geocoder.geocode_pois,
        arcgis_geocoder.geocode_pois
    ]
    
    evaluation_results = []
    
    for geocode_func in geocoders:
        # Run geocoding
        result_dict = geocode_func(pois, city, country, api_key=google_api_key)
        
        # Calculate stats
        name = result_dict["name"]
        hits = result_dict["hits"]
        total = result_dict["total"]
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        print(f"-> {name}: Found {hits}/{total} ({hit_rate:.1f}%)")
        evaluation_results.append(result_dict)
        
    return evaluation_results

def main():
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    city = "Porto"
    country = "Portugal"
    
    pois_file = os.path.join(config.STORY_OUTPUT, "porto_trajectory_pois.json")
    
    if not os.path.exists(pois_file):
        print(f"Error: {pois_file} not found. Run test_05 first.")
        return

    with open(pois_file, "r", encoding="utf-8") as f:
        pois = json.load(f)

    if not pois:
        print("No POIs found for geocoding.")
        return

    results = evaluate_geocoders(pois, google_api_key, city, country)
    
    out_file = os.path.join(config.STORY_OUTPUT, "porto_geocoders_evaluation.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print(f"\nEvaluation complete! Detailed results saved to: {out_file}")

if __name__ == "__main__":
    main()
