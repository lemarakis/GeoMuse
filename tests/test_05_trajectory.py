import os
import json
import config
from story.trajectory_story_generator import generate_story_from_trajectory
from story.poi_extractor import extract_pois_from_story
from visualization.trajectory_plotter import plot_trajectory_with_pois
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Παραγωγή story από το CSV
    trajectory_csv = os.path.join(config.BASE_DIR, "sstd2025", "trajectory.csv")
    if not os.path.exists(trajectory_csv):
        print(f"Error: {trajectory_csv} not found.")
        return

    print("\n=== STEP 1: Trajectory Story Generation ===")
    story = generate_story_from_trajectory(api_key, trajectory_csv)
    
    # Αποθήκευση story
    os.makedirs(config.STORY_OUTPUT, exist_ok=True)
    story_file = os.path.join(config.STORY_OUTPUT, "porto_trajectory_story.txt")
    with open(story_file, "w", encoding="utf-8") as f:
        f.write(story)
    
    print("\n--- TRAJECTORY STORY ---\n")
    try:
        print(story)
    except UnicodeEncodeError:
        print(story.encode('ascii', 'ignore').decode('ascii'))
    print(f"\nStory saved to {story_file}")

    print("\n=== STEP 2: POI Extraction from Trajectory Story ===")
    pois = extract_pois_from_story(api_key, story)
    
    # Αποθήκευση POIs
    pois_file = os.path.join(config.STORY_OUTPUT, "porto_trajectory_pois.json")
    with open(pois_file, "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=4)
    
    print(f"\nExtracted {len(pois)} POIs.")

    print("\n=== STEP 3: Trajectory Visualization ===")
    output_map = os.path.join(config.STORY_OUTPUT, "porto_trajectory_map.png")
    plot_trajectory_with_pois(trajectory_csv, pois, output_map, city="Porto")
    
    print(f"\nPipeline complete! Check the result at: {output_map}")


if __name__ == "__main__":
    main()
