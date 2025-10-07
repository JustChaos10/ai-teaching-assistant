from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from teacher_chatbot_app import TeacherChatbot
from pathlib import Path
import uuid, shutil

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = TeacherChatbot(murf_api_key="ap2_5f202fde-8bb8-41c2-a021-81c8757d64b9")

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/")
async def home():
    return {"status": "Teacher Chatbot API is running"}

# ---------------- Standard ask endpoint ----------------
@app.post("/ask")
async def ask(file: UploadFile):
    try:
        input_audio = OUTPUT_DIR / f"{uuid.uuid4()}.wav"
        with open(input_audio, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = chatbot.pipeline(str(input_audio))

        return JSONResponse({
            "question": result["question"],
            "answer": result["answer"],
            "audio_url": f"/audio/{Path(result['audio_url']).name}",
            "phonemes": result["phonemes"],
            "emotion": result["emotion"]
        })
    except Exception as e:
        return JSONResponse({"error": str(e)})

# ---------------- Serve TTS audio ----------------
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    audio_path = OUTPUT_DIR / filename
    if audio_path.exists():
        return FileResponse(audio_path)
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")
