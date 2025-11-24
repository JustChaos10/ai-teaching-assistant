from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
from teacher_chatbot_app import TeacherChatbot
from pathlib import Path
import uuid
import shutil
import os
import subprocess
import sys
from config import MURF_API_KEY, LECTURE_API_BASE, OUTPUT_DIR, IMAGES_DIR

SUPPORTED_STT_LANGUAGES = {"auto", "en", "ta"}

# ---------------- CONFIG ----------------
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI
app = FastAPI(title="AI Teaching Assistant Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow your frontend (e.g., localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for generated images
app.mount("/static", StaticFiles(directory="static"), name="static")

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
async def ask(file: UploadFile, language: str = "auto"):
    """
    Accepts a WAV file, transcribes the question (Tamil, English or auto-detect),
    generates an AI response, converts to TTS, and returns audio for the avatar.
    Optional query parameter `language` can be `auto`, `en`, or `ta`.
    """
    language_normalized = (language or "").strip().lower()
    if language_normalized not in SUPPORTED_STT_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{language}'. Choose from {sorted(SUPPORTED_STT_LANGUAGES)}."
        )

    try:
        input_audio = OUTPUT_DIR / f"{uuid.uuid4()}.wav"
        with open(input_audio, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = chatbot.pipeline(str(input_audio), language_hint=language_normalized)

        return JSONResponse({
            "mode": "qa",
            "question": result["question"],
            "answer": result["answer"],
            "language": result.get("language", "en"),
            "audio_url": f"/audio/{Path(result['audio_url']).name}",
            "emotion": result["emotion"],
            "images": result.get("images", [])  # Include generated images
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
    to speech and returns audio URL.
    """
    try:
        data = await request.json()
        text = data.get("text")
        if not text:
            raise HTTPException(status_code=400, detail="Missing 'text' field")

        tts_file = chatbot.tts(text)

        return JSONResponse({
            "mode": "speak",
            "text": text,
            "audio_url": f"/audio/{Path(tts_file).name}",
            "emotion": "neutral"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")

# ------------------- GAMES LAUNCHER -------------------
@app.post("/launch-games")
async def launch_games():
    """
    Launches the Games/main.py script which opens the game launcher GUI.
    """
    import traceback
    try:
        # Get the path to the Games directory
        games_dir = Path(__file__).parent.parent / "Games"
        main_py = games_dir / "main.py"

        print(f"[DEBUG] Backend dir: {Path(__file__).parent}")
        print(f"[DEBUG] Games dir: {games_dir}")
        print(f"[DEBUG] Main.py path: {main_py}")
        print(f"[DEBUG] Main.py exists: {main_py.exists()}")
        print(f"[DEBUG] Python executable: {sys.executable}")

        if not main_py.exists():
            error_msg = f"Games launcher not found at {main_py}"
            print(f"[ERROR] {error_msg}")
            raise HTTPException(status_code=404, detail=error_msg)

        # Launch the game launcher in a new process.
        # Use the current Python executable for reliability.
        print(f"[DEBUG] Launching subprocess...")
        if os.name == "nt":
            # Windows: Launch without console window (GUI only)
            process = subprocess.Popen(
                [sys.executable, str(main_py)],
                cwd=str(games_dir),
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            print(f"[DEBUG] Process launched with PID: {process.pid}")
        else:
            # POSIX: Detach from parent process
            process = subprocess.Popen(
                [sys.executable, str(main_py)],
                cwd=str(games_dir),
                start_new_session=True,
            )
            print(f"[DEBUG] Process launched with PID: {process.pid}")

        return JSONResponse({
            "status": "success",
            "message": "Games launcher started successfully"
        })

    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error launching games: {str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create-games")
async def create_games():
    """
    Launches the Games/create_game.py script which opens the game creator GUI.
    """
    import traceback
    try:
        # Get the path to the Games directory
        games_dir = Path(__file__).parent.parent / "Games"
        create_game_py = games_dir / "create_game.py"

        print(f"[DEBUG] Backend dir: {Path(__file__).parent}")
        print(f"[DEBUG] Games dir: {games_dir}")
        print(f"[DEBUG] create_game.py path: {create_game_py}")
        print(f"[DEBUG] create_game.py exists: {create_game_py.exists()}")
        print(f"[DEBUG] Python executable: {sys.executable}")

        if not create_game_py.exists():
            error_msg = f"Game creator not found at {create_game_py}"
            print(f"[ERROR] {error_msg}")
            raise HTTPException(status_code=404, detail=error_msg)

        # Launch the game creator in a new process.
        print(f"[DEBUG] Launching game creator subprocess...")
        if os.name == "nt":
            # Windows: Launch without console window (GUI only)
            process = subprocess.Popen(
                [sys.executable, str(create_game_py)],
                cwd=str(games_dir),
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            print(f"[DEBUG] Game creator launched with PID: {process.pid}")
        else:
            # POSIX: Detach from parent process
            process = subprocess.Popen(
                [sys.executable, str(create_game_py)],
                cwd=str(games_dir),
                start_new_session=True,
            )
            print(f"[DEBUG] Game creator launched with PID: {process.pid}")

        return JSONResponse({
            "status": "success",
            "message": "Game creator started successfully"
        })

    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error launching game creator: {str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))

