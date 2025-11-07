from pathlib import Path
import os

# Path to Rhubarb executable
RHUBARB_PATH = Path(r"C:\tools\rhubarb\rhubarb.exe")

# Murf AI API Key - It's better to use environment variables for sensitive keys
MURF_API_KEY = os.getenv("MURF_API_KEY", "ap2_5f202fde-8bb8-41c2-a021-81c8757d64b9")

# API endpoint for the external lecture service
LECTURE_API_BASE = "http://localhost:5000/api"

# Directory for storing output files (audio, phonemes, etc.)
OUTPUT_DIR = Path("outputs")