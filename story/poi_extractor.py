import os
import json
from google import genai
from dotenv import load_dotenv

import config
from prompts import POI_EXTRACTION_PROMPT_UNBIASED

load_dotenv()

def extract_pois_from_story(api_key: str, story: str) -> list:
    client = genai.Client(api_key=api_key)

    prompt = POI_EXTRACTION_PROMPT_UNBIASED.format(story=story)
    gen_config = {
        "temperature": 0.1,
        "response_mime_type": "application/json"
    }

    print(f" -> Extracting POIs from story...")
    
    response = client.models.generate_content(
        model=config.MODEL_EXTRACTION,
        contents=prompt,
        config=gen_config
    )

    try:
        raw_text = response.text
        # Clean markdown if present
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
        
        pois = json.loads(raw_text)
        return pois
    except json.JSONDecodeError:
        print("Error decoding JSON from Gemini response:")
        print(response.text)
        return []

if __name__ == "__main__":
    # Test extraction
    api_key = os.getenv("GEMINI_API_KEY")
    test_story = """
    Your journey begins at Sao Bento Station, famous for its tiles. 
    Then you head to Clerigos Tower and the beautiful Livraria Lello.
    """
    pois = extract_pois_from_story(api_key, test_story)
    print(json.dumps(pois, indent=4, ensure_ascii=False))
