import os
import uuid
import subprocess
import requests
import pygame
from murf import Murf
from faster_whisper import WhisperModel
from pathlib import Path
from rag_system import RAGSystem
from teacher_chatbot import auto_ingest_docs, clean_text
from config import RHUBARB_PATH, OUTPUT_DIR


pygame.mixer.init()


class TeacherChatbot:
    def __init__(self, murf_api_key, docs_folder="./docs"):
        self.murf_api_key = murf_api_key
        self.stt_model = WhisperModel("small", device="cpu", compute_type="int8")  # Whisper model
        
        # ---------------- RAG SYSTEM ----------------
        self.rag = RAGSystem()
        auto_ingest_docs(self.rag, docs_folder)

    # ---------------- STT ----------------
    def stt(self, audio_path):
        segments, _ = self.stt_model.transcribe(audio_path)
        text = " ".join([seg.text for seg in segments]).strip()
        return text or "Could not understand"

    # ---------------- Chatbot (RAG query) ----------------
    def query_chatbot(self, question):
        question_cleaned = clean_text(question)
        try:
            answer = self.rag.query(question_cleaned)
        except Exception as e:
            answer = f"Sorry, I couldn't answer that. ({e})"
        emotion = "neutral"
        return answer, emotion

    # ---------------- TTS ----------------
    def tts(self, text):
        client = Murf(api_key=self.murf_api_key)
        response = client.text_to_speech.generate(text=text, voice_id="en-US-charles")
        audio_url = response.audio_file
        
        local_file = OUTPUT_DIR / f"{uuid.uuid4()}.wav"
        r = requests.get(audio_url)
        with open(local_file, "wb") as f:
            f.write(r.content)
            
        return local_file

    # ---------------- Rhubarb Lip Sync ----------------
    def generate_lipsync(self, audio_file):
        if not RHUBARB_PATH.exists():
            raise FileNotFoundError(
                f"Rhubarb executable not found at {RHUBARB_PATH}. "
                "Please download Rhubarb from https://github.com/DanielSWolf/rhubarb-lip-sync/releases "
                "and place it at the specified path, or update RHUBARB_PATH in config.py."
            )
        json_file = OUTPUT_DIR / f"{uuid.uuid4()}.json"
        cmd = [
            str(RHUBARB_PATH),   # Path to rhubarb.exe
            "-f", "json",        # Output format: json
            str(audio_file),     # Input audio file
            "-o", str(json_file)  # Output JSON file
        ]
        subprocess.run(cmd, check=True)
        return json_file

    # ---------------- Full pipeline ----------------
    def pipeline(self, audio_path):
        question = self.stt(audio_path)
        answer, emotion = self.query_chatbot(question)
        tts_file = self.tts(answer)
        phonemes_file = self.generate_lipsync(tts_file)
        
        import json
        with open(phonemes_file, "r") as f:
            phonemes = json.load(f)
            
        return {
            "question": question,
            "answer": answer,
            "audio_url": str(tts_file),
            "phonemes": phonemes,
            "emotion": emotion
        }
