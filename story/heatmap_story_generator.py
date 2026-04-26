import os
from PIL import Image
from google import genai
from dotenv import load_dotenv

import config
from prompts import HEATMAP_VISITOR_PROMPT, HEATMAP_PROFESSIONAL_PROMPT, HEATMAP_UNBIASED_PROMPT, ATHENS_VISITOR_PROMPT

load_dotenv()

def generate_story_from_heatmap(api_key: str, image_path: str, audience: str = "visitor") -> str:
    client = genai.Client(api_key=api_key)
    img = Image.open(image_path)
    
    if audience == "professional":
        prompt = HEATMAP_PROFESSIONAL_PROMPT
    elif audience == "unbiased":
        prompt = HEATMAP_UNBIASED_PROMPT
    elif audience == "athens_visitor":
        prompt = ATHENS_VISITOR_PROMPT
    else:
        prompt = HEATMAP_VISITOR_PROMPT

    print(f" -> Calling Gemini ({config.MODEL_GENERATION}) for {audience} story...")
    
    response = client.models.generate_content(
        model=config.MODEL_GENERATION,
        contents=[prompt, img],
        config={
            "temperature": 0.7
        }
    )

    return response.text

if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    test_image = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto_overlay.png")
    
    if os.path.exists(test_image):
        story = generate_story_from_heatmap(api_key, test_image, audience="visitor")
        print("\n--- GENERATED STORY ---\n")
        print(story)
