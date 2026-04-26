import os
import json
from dotenv import load_dotenv

import config
from utils.places_fetcher import sample_trajectory_points, get_nearby_pois
from agents.control_agent import run_agent

def main():
    trajectory_csv = os.path.join(config.BASE_DIR, "sstd2025", "trajectory.csv")
    image_path = os.path.join(config.STORY_OUTPUT, "porto_trajectory_map.png")
    output_json = os.path.join(config.STORY_OUTPUT, "porto_agentic_rag_story.json")
    
    if not os.path.exists(trajectory_csv) or not os.path.exists(image_path):
        print("Error: Missing trajectory or map image. Run test_05 first.")
        return

    load_dotenv()
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    # Fetch real POIs along the route
    print("=== Sampling Trajectory ===")
    sampled_points = sample_trajectory_points(trajectory_csv, interval_meters=500.0)
    print(f"Sampled {len(sampled_points)} points along the route.")

    print("=== Fetching Real POIs via Google Places ===")
    all_real_pois = []
    seen_names = set()
    
    for lat, lon in sampled_points:
        pois = get_nearby_pois(lat, lon, google_api_key, radius=100, types="restaurant|store|point_of_interest|park", max_results=1)
        for p in pois:
            if p["name"] not in seen_names:
                all_real_pois.append(p)
                seen_names.add(p["name"])
                
    print(f"Found {len(all_real_pois)} unique real POIs along the route.")

    # Trigger the Control Agent with RAG POIs
    print("\n=== Starting Agentic RAG Workflow ===")
    final_story = run_agent(
        trajectory_csv=trajectory_csv, 
        image_path=image_path, 
        city="Porto", 
        threshold_meters=200.0, 
        max_retries=3,
        rag_pois=all_real_pois
    )

    if final_story:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(final_story, f, ensure_ascii=False, indent=4)
        print(f"\n[SYSTEM] Final Agentic RAG story saved to {output_json}")
        
        pois_data = final_story.get("pois", [])
        if pois_data:
            from visualization.trajectory_deviation_plotter import plot_trajectory_deviation
            map_filename = output_json.replace(".json", "_map.png")
            print(f"[SYSTEM] Generating deviation map: {map_filename}")
            plot_trajectory_deviation(trajectory_csv, pois_data, map_filename, city="Porto", use_llm_coords=True)

if __name__ == "__main__":
    main()
