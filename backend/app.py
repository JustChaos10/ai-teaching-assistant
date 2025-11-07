from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from teacher_chatbot_app import TeacherChatbot
from pathlib import Path
import uuid
import shutil
import os
from config import MURF_API_KEY, LECTURE_API_BASE, OUTPUT_DIR

# ---------------- CONFIG ----------------
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize FastAPI
app = FastAPI(title="AI Teaching Assistant Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow your frontend (e.g., localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CHATBOT INIT ----------------
chatbot = TeacherChatbot(
    murf_api_key=MURF_API_KEY
)

# ---------------- ROOT ----------------
@app.get("/")
async def home():
    return {"status": "AI Teaching Assistant API is running"}

# ------------------- Q&A MODE (AUDIO INPUT) -------------------
@app.post("/ask")
async def ask(file: UploadFile):
    """
    Accepts a WAV file, transcribes the question,
    generates an AI response, converts to TTS, and returns
    phoneme animation + audio for the avatar.
    """
    try:
        input_audio = OUTPUT_DIR / f"{uuid.uuid4()}.wav"
        with open(input_audio, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = chatbot.pipeline(str(input_audio))

        return JSONResponse({
            "mode": "qa",
            "question": result["question"],
            "answer": result["answer"],
            "audio_url": f"/audio/{Path(result['audio_url']).name}",
            "phonemes": result["phonemes"],
            "emotion": result["emotion"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ------------------- SERVE AUDIO FILES -------------------
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    audio_path = OUTPUT_DIR / filename
    if audio_path.exists():
        return FileResponse(audio_path)
    raise HTTPException(status_code=404, detail="Audio file not found")

# ================================================================
# LECTURE MODE (FOR SUMMARIZATION + QUIZZES)
# Proxies to the Node.js routes.ts API
# ================================================================

@app.get("/lectures")
async def list_lectures():
    """Get all lectures."""
    try:
        r = requests.get(f"{LECTURE_API_BASE}/lectures", timeout=20)
        return JSONResponse(r.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lectures: {e}")

@app.get("/lectures/{lecture_id}")
async def get_lecture(lecture_id: str):
    """Get details of one lecture."""
    try:
        r = requests.get(f"{LECTURE_API_BASE}/lectures/{lecture_id}", timeout=20)
        return JSONResponse(r.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lecture: {e}")

@app.post("/lectures")
async def create_lecture(request: Request):
    """
    Create a new lecture (teacher uploads text content).
    This automatically triggers summarization and quiz generation
    through the Node.js lecture API.
    """
    try:
        payload = await request.json()
        r = requests.post(f"{LECTURE_API_BASE}/lectures", json=payload, timeout=60)
        return JSONResponse(r.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating lecture: {e}")

@app.post("/quizzes/generate")
async def generate_quiz(request: Request):
    """Generate quiz questions for a lecture."""
    try:
        payload = await request.json()
        r = requests.post(f"{LECTURE_API_BASE}/quizzes/generate", json=payload, timeout=60)
        return JSONResponse(r.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {e}")

# ------------------- TTS FOR SUMMARIES -------------------
@app.post("/speak")
async def speak(request: Request):
    """
    Converts provided text (e.g., lecture summary or answer)
    to speech and returns audio URL + phoneme animation data.
    """
    try:
        data = await request.json()
        text = data.get("text")
        if not text:
            raise HTTPException(status_code=400, detail="Missing 'text' field")

        tts_file = chatbot.tts(text)
        phonemes_file = chatbot.generate_lipsync(tts_file)

        import json
        with open(phonemes_file, "r") as f:
            phonemes = json.load(f)

        return JSONResponse({
            "mode": "speak",
            "text": text,
            "audio_url": f"/audio/{Path(tts_file).name}",
            "phonemes": phonemes,
            "emotion": "neutral"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")

