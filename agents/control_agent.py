import os
import json
import base64
from dotenv import load_dotenv

from google import genai
from google.genai import types
import prompts
from geocoders.google_geocoder import geocode_pois
from utils.deviation_math import calculate_average_deviation

def _generate_story_with_feedback(image_path: str, base_prompt: str, feedback: str = None) -> dict:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    image_part = types.Part.from_bytes(
        data=base64.b64decode(encoded_string),
        mime_type='image/png'
    )

    final_prompt = base_prompt
    if feedback:
        final_prompt += f"\n\n[VALIDATION FEEDBACK]: {feedback}"

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[image_part, final_prompt],
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)


def run_agent(trajectory_csv: str, image_path: str, city: str, threshold_meters: float = 200.0, max_retries: int = 3, rag_pois: list = None) -> dict:
    """
    Main Agent
    """
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    print(f"\n[CONTROL AGENT] Starting workflow for {city}")
    print(f"[CONTROL AGENT] Target Deviation: < {threshold_meters} meters. Max Retries: {max_retries}")
    
    if rag_pois:
        print("[CONTROL AGENT] Operating in RAG Mode (Spatial Grounding Enabled).")
        base_prompt = prompts.GROUNDED_TRAJECTORY_STORY_PROMPT + "\n\n" + json.dumps(rag_pois, indent=2)
    else:
        print("[CONTROL AGENT] Operating in Default Mode (No Grounding).")
        base_prompt = prompts.AGENTIC_STORY_PROMPT

    attempts = 0
    feedback = None
    best_story_json = None
    best_comparison_data = None
    best_deviation = float('inf')

    while attempts < max_retries:
        print(f"\n--- ATTEMPT {attempts + 1} / {max_retries} ---")
        
        # 1. Story Generation LLM
        print("[AGENT] Generating story...")
        story_json = _generate_story_with_feedback(image_path, base_prompt, feedback)
        
        llm_pois = story_json.get("pois", [])
        if not llm_pois:
            feedback = "You failed to extract any POIs. Please ensure you output the JSON correctly."
            attempts += 1
            continue
            
        print(f"[AGENT] Extracted {len(llm_pois)} POIs from story.")
        
        # 2. Validation Agent (Geocode & Math)
        print("[AGENT] Validating geographic accuracy...")
        result_dict = geocode_pois(llm_pois, city, "Portugal", api_key=google_api_key)
        comparison_data = result_dict["results"]
        
        is_rag_mode = bool(rag_pois)
        avg_deviation = calculate_average_deviation(trajectory_csv, comparison_data, use_llm_coords=is_rag_mode)
        print(f"[AGENT] Average Deviation: {avg_deviation:.1f} meters")
        
        if avg_deviation < best_deviation:
            best_deviation = avg_deviation
            best_story_json = story_json
            best_comparison_data = comparison_data

        # 3. Decision (The Feedback Loop)
        if avg_deviation <= threshold_meters:
            print("[CONTROL AGENT] Validation PASSED! The story is geographically accurate.")
            story_json["pois"] = comparison_data
            return story_json
        else:
            print(f"[CONTROL AGENT] Validation FAILED (Threshold is {threshold_meters}m). Triggering rewrite...")
            feedback = (
                f"Your previous story FAILED the geographic validation test. "
                f"The places you chose were on average {avg_deviation:.1f} meters away from the red line. "
                f"You MUST look closer at the red line and choose places that are strictly underneath it. "
                f"Do not guess famous landmarks if they are not on the line."
            )
            attempts += 1

    print(f"\n[CONTROL AGENT] Reached max retries ({max_retries}). Returning the best story found (Deviation: {best_deviation:.1f}m).")
    if best_story_json and best_comparison_data is not None:
        best_story_json["pois"] = best_comparison_data
        
    return best_story_json
