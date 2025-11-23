from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Murf AI API Key - It's better to use environment variables for sensitive keys
MURF_API_KEY = os.getenv("MURF_API_KEY", "ap2_5f202fde-8bb8-41c2-a021-81c8757d64b9")

# Murf voices per language (default to English voice; override via env for Tamil)
MURF_VOICE_EN = os.getenv("MURF_VOICE_EN", "en-US-charles")
MURF_VOICE_TA = os.getenv("MURF_VOICE_TA", "ta-IN-suresh")

# API endpoint for the external lecture service
LECTURE_API_BASE = "http://localhost:5000/api"

# Directory for storing output files (audio, etc.)
OUTPUT_DIR = Path("outputs")

# Image Generation API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # For analyzing content and creating prompts
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")  # For FLUX Schnell image generation

# Directory for generated images
IMAGES_DIR = Path("static/generated_images")
