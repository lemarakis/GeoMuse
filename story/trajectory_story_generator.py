import os
from google import genai
from dotenv import load_dotenv

import config
from prompts import TRAJECTORY_STORY_PROMPT

load_dotenv()

def generate_story_from_trajectory(api_key: str, csv_path: str) -> str:
    client = genai.Client(api_key=api_key)
    
    if not os.path.exists(csv_path):
        return f"Error: CSV file not found at {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        csv_content = f.read()

    print(f" -> Calling Gemini ({config.MODEL_GENERATION}) for trajectory story...")
    
    full_prompt = f"{TRAJECTORY_STORY_PROMPT}\n\nCSV Data:\n{csv_content}"
    
    response = client.models.generate_content(
        model=config.MODEL_GENERATION,
        contents=full_prompt,
        config={
            "temperature": 0.7
        }
    )

    return response.text

if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    trajectory_csv = os.path.join(config.BASE_DIR, "sstd2025", "trajectory.csv")
    
    if os.path.exists(trajectory_csv):
        story = generate_story_from_trajectory(api_key, trajectory_csv)
        print("\n--- TRAJECTORY STORY ---\n")
        print(story)
