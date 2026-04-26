import os
import json
import base64
from dotenv import load_dotenv

from google import genai
from google.genai import types

import config
import prompts
from utils.places_fetcher import sample_trajectory_points, get_nearby_pois
from geocoders.google_geocoder import geocode_pois
from tests.test_12_trajectory_deviation import calculate_trajectory_deviation

def generate_grounded_story(image_path: str, real_pois: list) -> dict:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    image_part = types.Part.from_bytes(
        data=base64.b64decode(encoded_string),
        mime_type='image/png'
    )

    # Format the real POIs for the prompt, including their real coordinates
    poi_list_str = "\n".join([f"- {p['name']} ({', '.join(p['types'])}), lon: {p['lon']}, lat: {p['lat']}" for p in real_pois])

    prompt = prompts.GROUNDED_TRAJECTORY_STORY_PROMPT.format(poi_list_str=poi_list_str)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[image_part, prompt],
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)


def main():
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    trajectory_csv = os.path.join(config.BASE_DIR, "sstd2025", "trajectory.csv")
    image_path = os.path.join(config.STORY_OUTPUT, "porto_trajectory_map.png")
    
    if not os.path.exists(trajectory_csv) or not os.path.exists(image_path):
        print("Missing trajectory files. Run test_05 first.")
        return

    # Sample the trajectory
    print("=== Sampling Trajectory ===")
    sampled_points = sample_trajectory_points(trajectory_csv, interval_meters=500.0)
    print(f"Sampled {len(sampled_points)} points along the route.")

    # Fetch real POIs
    print("=== Fetching Real POIs via Google Places ===")
    all_real_pois = []
    seen_names = set()
    
    for lat, lon in sampled_points:
        pois = get_nearby_pois(lat, lon, google_api_key, radius=100, types="restaurant|store|point_of_interest|park", max_results=1)
        for p in pois:
            if p["name"] not in seen_names:
                all_real_pois.append(p)
                seen_names.add(p["name"])
                
    print(f"Found {len(all_real_pois)} unique real POIs along the route:")
    for p in all_real_pois:
        safe_name = p['name'].encode('ascii', 'ignore').decode('ascii')
        print(f" - {safe_name}")

    # Generate Grounded Story
    print("\n=== Generating Grounded Story ===")
    story_json = generate_grounded_story(image_path, all_real_pois)
    
    story_file = os.path.join(config.STORY_OUTPUT, "porto_grounded_story.json")
    with open(story_file, "w", encoding="utf-8") as f:
        json.dump(story_json, f, ensure_ascii=False, indent=4)
        
    print(f"Story saved to {story_file}")

    llm_pois = story_json.get("pois", [])
    if not llm_pois:
        print("No POIs extracted by LLM.")
        return
        
    print(f"\n=== Geocoding {len(llm_pois)} Grounded POIs ===")
    result_dict = geocode_pois(llm_pois, "Porto", "Portugal", api_key=google_api_key)
    comparison_data = result_dict["results"]
    
    comparison_json = os.path.join(config.STORY_OUTPUT, "porto_grounded_google_comparison.json")
    with open(comparison_json, "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, ensure_ascii=False, indent=4)
        
    # Calculate Trajectory Deviation & Generate Map
    output_json = os.path.join(config.STORY_OUTPUT, "porto_grounded_trajectory_deviation.json")
    calculate_trajectory_deviation(trajectory_csv, comparison_json, output_json)
    
    # Generate Map
    from visualization.trajectory_deviation_plotter import plot_trajectory_deviation
    
    with open(output_json, "r", encoding="utf-8") as f:
        deviation_data = json.load(f)
        
    map_filename = os.path.join(config.STORY_OUTPUT, "porto_grounded_trajectory_deviation_map.png")
    plot_trajectory_deviation(trajectory_csv, deviation_data, map_filename, city="Porto (Grounded)")

if __name__ == "__main__":
    main()
