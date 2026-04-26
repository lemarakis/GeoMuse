import os


# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMON_DIR = os.path.join(BASE_DIR, "common")
HEATMAP_OUTPUT = os.path.join(COMMON_DIR, "heatmaps")
STORY_OUTPUT = os.path.join(COMMON_DIR, "stories")

# STORY GENERATION
MODEL_GENERATION = "gemini-2.5-flash"

# EXTRACT POIs
MODEL_EXTRACTION = "gemini-2.5-flash"

