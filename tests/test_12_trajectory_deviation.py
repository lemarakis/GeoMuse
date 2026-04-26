import os
import json
import config

def calculate_trajectory_deviation(trajectory_csv: str, comparison_json: str, output_json: str):
    if not os.path.exists(trajectory_csv):
        print(f"Error: Trajectory CSV not found at {trajectory_csv}")
        return
        
    if not os.path.exists(comparison_json):
        print(f"Error: Comparison JSON not found at {comparison_json}. Run test_10 first.")
        return


    # Load Comparison Data (API real-world coordinates)
    with open(comparison_json, "r", encoding="utf-8") as f:
        pois = json.load(f)

    if not pois:
        print("No POIs found in comparison JSON.")
        return

    print("=== Calculating Deviation from Actual Trajectory ===")
    from utils.deviation_math import calculate_average_deviation
    
    calculate_average_deviation(trajectory_csv, pois, print_results=True)

    # Save the updated JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=4)
        
    print(f"Deviation data saved to: {output_json}")
    
    # Generate Map
    from visualization.trajectory_deviation_plotter import plot_trajectory_deviation
    map_filename = output_json.replace(".json", "_map.png")
    plot_trajectory_deviation(trajectory_csv, pois, map_filename, city="Porto")

def main():
    trajectory_csv = os.path.join(config.BASE_DIR, "sstd2025", "trajectory.csv")
    comparison_json = os.path.join(config.STORY_OUTPUT, "porto_trajectory_google_comparison.json")
    output_json = os.path.join(config.STORY_OUTPUT, "porto_trajectory_deviation.json")
    
    calculate_trajectory_deviation(trajectory_csv, comparison_json, output_json)

if __name__ == "__main__":
    main()
