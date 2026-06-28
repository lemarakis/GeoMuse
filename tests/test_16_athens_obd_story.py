import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from story.obd_story_generator import generate_obd_story, plot_obd_trajectory

def main():
    # Load env variables
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not gemini_api_key:
        print("[ERROR] GEMINI_API_KEY is not defined in the environment.")
        return
        
    if not google_api_key:
        print("[ERROR] GOOGLE_MAPS_API_KEY is not defined in the environment.")
        return
        
    trajectory_csv = os.path.join(config.BASE_DIR, "sstd2025", "Athens-obd-2.csv")
    if not os.path.exists(trajectory_csv):
        print(f"[ERROR] Athens OBD CSV not found at: {trajectory_csv}")
        return
        
   
    # 1. Generate Story & analyze events
    story, analysis = generate_obd_story(gemini_api_key, google_api_key, trajectory_csv)
    
    # Save Story text
    os.makedirs(config.STORY_OUTPUT, exist_ok=True)
    story_file = os.path.join(config.STORY_OUTPUT, "athens_obd_story.txt")
    with open(story_file, "w", encoding="utf-8") as f:
        f.write(story)
        
    try:
        print(story)
    except UnicodeEncodeError:
        print(story.encode('ascii', 'ignore').decode('ascii'))
    
    # 2. Plot Trajectory Map
    map_image = os.path.join(config.STORY_OUTPUT, "athens_obd_trajectory_map.png")
    plot_obd_trajectory(analysis, map_image, city="Athens")
    
    print("\n=== OK ===")
    print(f"Generated text: {story_file}")
    print(f"Generated map: {map_image}")

if __name__ == "__main__":
    main()
