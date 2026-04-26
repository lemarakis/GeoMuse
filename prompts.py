
HEATMAP_PROFESSIONAL_PROMPT = """
I will provide a png image that represents a heat map
of taxi endpoints in the city of Porto, Portugal. Describe the data in
a neutral professional tone. Use technical terms. Use storytelling
techniques. Include at least 15 POIs. Highlight the POIs. Use at most
150 words.
"""

HEATMAP_VISITOR_PROMPT = """
I will provide a png image that presents a heat map
of taxi endpoints in the city of Porto, Portugal.
Write a story about the data using cinematic storytelling techniques.
Your target audience is a first time visitor of the city.
Include at least 15 POIs. Highlight the POIs.
Include some useful information about the POIs. Use at most 250 words.
"""

ATHENS_VISITOR_PROMPT = """
I will provide a png image that presents a heat map
of taxi endpoints in the city of Athens, Greece.
Write a story about the data using cinematic storytelling techniques.
Your target audience is a first time visitor of the city.
Include at least 15 POIs. Highlight the POIs.
Include some useful information about the POIs. Use at most 250 words.
"""

HEATMAP_UNBIASED_PROMPT = """
I will provide a PNG image representing a taxi activity heatmap. 

Your task is to act as an unbiased Geospatial Storyteller:
1. Identify the city and country shown in the base map.
2. Visually scan the image to find the exact area(s) where the bright heatmap color density is highest (the "hotspots"). 
3. Note the geographic position of these specific hotspots.
4. Extract at least 15 POIs, landmarks, hospitals, or streets that are located EXACTLY underneath these visible hotspots. 

CRITICAL INSTRUCTION: You must absolutely ignore famous city landmarks or downtown tourist areas if they appear in dark areas with no heatmap activity. 
I am interested ONLY in the specific neighborhoods and locations where the bright glowing data actually exists on this specific map. 

Based strictly on the legitimate hotspots you found, write a story about the data using cinematic storytelling techniques. 
Your target audience is a first time visitor of this area. 
Include some useful information about the extracted POIs. Highlight the POIs in your text. Use at most 250 words.
"""

POI_EXTRACTION_PROMPT_UNBIASED = """
Read the following story about a taxi trip or heatmap.
Extract the names of all the specific geographic Points of Interest (POIs), landmarks, 
stations, parks, or specific monuments mentioned in the text.
For each POI, use your internal knowledge to provide its approximate Longitude and Latitude based on the city it belongs to.

Return ONLY a valid JSON array of objects. No markdown formatting, no explanations.
Example: 
[
  {{"name": "São Bento Station", "lon": -8.61099, "lat": 41.14557}},
  {{"name": "Clérigos Tower", "lon": -8.6142, "lat": 41.1456}}
]
Story:
{story}
"""

TRAJECTORY_STORY_PROMPT = """
I will provide a cvs file that contains a list of points
(longitude, latitude), that describe a trajectory of a taxi trip. Using
cinematic storytelling write a story about the trajectory. Mention
explicitly major road names, intersections, neighborhoods, local
POIs (e.g., restaurant name). Use 150 words maximum.
"""


GROUNDED_TRAJECTORY_STORY_PROMPT = """
You are an expert spatio-temporal storyteller. 
I am providing you with an image of a map showing a taxi trajectory (the red line).
I am also providing you with a list of REAL places that this taxi passed by along its route, including their exact coordinates:

{poi_list_str}

Write a realistic, engaging story about a passenger taking this taxi ride.
CRITICAL INSTRUCTION: You MUST incorporate ALL of the places listed above in your story, in the exact order they are listed. 
Do NOT invent any other specific named locations, streets, or landmarks. 
Your story must be STRICTLY grounded on these provided places to avoid geographic hallucinations.

Output the story and extract the exact places you mentioned into the following JSON format.
CRITICAL: You MUST use the exact longitude (lon) and latitude (lat) provided to you in the list above for each place! Do not output 0.0.

{{
    "title": "Story Title",
    "story": "The full text of the story...",
    "pois": [
        {{"name": "Place Name 1", "lon": -8.61, "lat": 41.15}},
        {{"name": "Place Name 2", "lon": -8.62, "lat": 41.16}}
    ]
}}
Provide the JSON only. Do not include markdown blocks or any other text.
"""

AGENTIC_STORY_PROMPT = """
I will provide a PNG image representing a map with a red taxi trajectory. 
Write a cinematic story about a passenger taking this taxi ride.
Extract the specific places, streets, or parks mentioned into the following JSON format:
{
    "title": "Story Title",
    "story": "The full text of the story...",
    "pois": [
        {"name": "Place Name 1", "lon": 0.0, "lat": 0.0}
    ]
}
Provide JSON only.
"""

