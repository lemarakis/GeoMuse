import os
import json
import config
from story.heatmap_story_generator import generate_story_from_heatmap
from story.poi_extractor import extract_pois_from_story
from visualization.poi_plotter import plot_pois
from dotenv import load_dotenv

def run_experiment(api_key, image_path, audience, suffix, city="Porto"):
    print(f"\n[EXPERIMENT] Audience: {audience} | Suffix: {suffix}")
    
    story = generate_story_from_heatmap(api_key, image_path, audience=audience)
    
    os.makedirs(config.STORY_OUTPUT, exist_ok=True)
    
    story_file = os.path.join(config.STORY_OUTPUT, f"porto_fake_story_{suffix}.txt")
    with open(story_file, "w", encoding="utf-8") as f:
        f.write(story)
    
    # Extract POIs
    pois = extract_pois_from_story(api_key, story)
    pois_file = os.path.join(config.STORY_OUTPUT, f"porto_fake_pois_{suffix}.json")
    with open(pois_file, "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=4)
        
    # Plot POIs
    map_file = os.path.join(config.STORY_OUTPUT, f"porto_fake_map_{suffix}.png")
    plot_pois(pois, map_file, city=city)
    
    print(f" -> Done. Results saved with suffix '{suffix}'")
    return story

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    fake_image = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto_fake.png")
    
    if not os.path.exists(fake_image):
        print(f"Error: {fake_image} not found. Run heatmap_fake_generator first.")
        return

    # TEST 1: Standard Visitor Prompt
    print("\n=== RUNNING TEST 1: STANDARD VISITOR PROMPT ===")
    run_experiment(api_key, fake_image, audience="visitor", suffix="standard", city="Porto")

    # TEST 2: Unbiased Prompt
    print("\n=== RUNNING TEST 2: UNBIASED PROMPT ===")
    run_experiment(api_key, fake_image, audience="unbiased", suffix="unbiased", city="Porto")

if __name__ == "__main__":
    main()
