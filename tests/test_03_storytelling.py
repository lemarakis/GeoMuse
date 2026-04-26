import os
import json
import config
from story.heatmap_story_generator import generate_story_from_heatmap
from story.poi_extractor import extract_pois_from_story
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    image_path = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto_overlay.png")
    
    if not os.path.exists(image_path):
        print(f"Heatmap image not found at {image_path}. Please run test_02 first.")
        return

    print("\n=== STEP 1: Story Generation ===")
    story = generate_story_from_heatmap(api_key, image_path, audience="visitor")
    
    os.makedirs(config.STORY_OUTPUT, exist_ok=True)
    story_file = os.path.join(config.STORY_OUTPUT, "porto_visitor_story.txt")
    with open(story_file, "w", encoding="utf-8") as f:
        f.write(story)
    
    print("\n--- GENERATED STORY ---\n")
    try:
        print(story)
    except UnicodeEncodeError:
        print(story.encode('ascii', 'ignore').decode('ascii'))
    print(f"\nStory saved to {story_file}")

    print("\n=== STEP 2: POI Extraction ===")
    pois = extract_pois_from_story(api_key, story)
    
    pois_file = os.path.join(config.STORY_OUTPUT, "porto_extracted_pois.json")
    with open(pois_file, "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=4)
    
    print(f"\nExtracted {len(pois)} POIs.")
    print(f"POIs saved to {pois_file}")
    
    for p in pois:
        name = p.get('name', 'N/A')
        try:
            print(f" - {name}: ({p.get('lat')}, {p.get('lon')})")
        except UnicodeEncodeError:
            print(f" - {name.encode('ascii', 'ignore').decode('ascii')}: ({p.get('lat')}, {p.get('lon')})")


if __name__ == "__main__":
    main()
