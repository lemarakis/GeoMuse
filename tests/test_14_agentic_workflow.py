import os
import json
import config

from agents.control_agent import run_agent

def main():
    trajectory_csv = os.path.join(config.BASE_DIR, "sstd2025", "trajectory.csv")
    image_path = os.path.join(config.STORY_OUTPUT, "porto_trajectory_map.png")
    output_json = os.path.join(config.STORY_OUTPUT, "porto_agentic_story.json")
    
    if not os.path.exists(trajectory_csv) or not os.path.exists(image_path):
        print("Error: Missing trajectory or map image. Run test_05 first.")
        return

    # Trigger the Control Agent (Threshold 200m, Max Retries 3)
    final_story = run_agent(
        trajectory_csv=trajectory_csv, 
        image_path=image_path, 
        city="Porto", 
        country="Portugal",
        threshold_meters=200.0, 
        max_retries=3
    )

    if final_story:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(final_story, f, ensure_ascii=False, indent=4)
        print(f"\n[SYSTEM] Final story saved to {output_json}")
        
        pois = final_story.get("pois", [])
        if pois:
            from visualization.trajectory_deviation_plotter import plot_trajectory_deviation
            map_filename = output_json.replace(".json", "_map.png")
            print(f"[SYSTEM] Generating deviation map: {map_filename}")
            plot_trajectory_deviation(trajectory_csv, pois, map_filename, city="Porto")

if __name__ == "__main__":
    main()
