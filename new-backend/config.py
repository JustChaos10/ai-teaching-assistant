from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Murf AI API Key - It's better to use environment variables for sensitive keys
MURF_API_KEY = os.getenv("MURF_API_KEY", "ap2_5f202fde-8bb8-41c2-a021-81c8757d64b9")

# Murf voices per language (default to English voice; override via env for Tamil)
MURF_VOICE_EN = os.getenv("MURF_VOICE_EN", "en-US-charles")
MURF_VOICE_TA = os.getenv("MURF_VOICE_TA", None)

# Warn if Tamil voice is not configured
if not MURF_VOICE_TA:
    print("[WARNING] MURF_VOICE_TA not set in .env file!")
    print("[WARNING] Tamil TTS will use English voice - this will sound incorrect!")
    print("[WARNING] To fix: Set MURF_VOICE_TA=ta-IN-<voice-name> in your .env file")
    print("[WARNING] Get Tamil voice IDs from: https://murf.ai/resources/voice-catalog")
    MURF_VOICE_TA = MURF_VOICE_EN  # Fallback to English voice

# API endpoint for the external lecture service
LECTURE_API_BASE = "http://localhost:5000/api"

# Directory for storing output files (audio, etc.)
OUTPUT_DIR = Path("outputs")

# Image Generation API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # For analyzing content and creating prompts
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")  # For FLUX Schnell image generation

# Directory for generated images
IMAGES_DIR = Path("static/generated_images")
