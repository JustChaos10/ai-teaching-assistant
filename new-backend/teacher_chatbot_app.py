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
from config import OUTPUT_DIR, MURF_VOICE_EN, MURF_VOICE_TA


pygame.mixer.init()


class TeacherChatbot:
    SUPPORTED_LANGUAGES = {"en", "ta"}

    def __init__(self, murf_api_key, docs_folder="./docs"):
        self.murf_api_key = murf_api_key
        self.stt_model = WhisperModel("small", device="cpu", compute_type="int8")  # Whisper model
        
        # ---------------- RAG SYSTEM ----------------
        self.rag = RAGSystem()
        auto_ingest_docs(self.rag, docs_folder)
        self.voice_map = {
            "en": MURF_VOICE_EN,
            "ta": MURF_VOICE_TA or MURF_VOICE_EN,
        }
        OUTPUT_DIR.mkdir(exist_ok=True)

    def _normalize_language(self, language_hint):
        if not language_hint:
            return None
        normalized = language_hint.strip().lower()
        if normalized == "auto":
            return None
        if normalized in self.SUPPORTED_LANGUAGES:
            return normalized
        return None

    def _resolve_response_language(self, normalized_hint, detected_language=None):
        if normalized_hint:
            return normalized_hint
        normalized_detected = self._normalize_language(detected_language)
        return normalized_detected or "en"

    # ---------------- STT ----------------
    def stt(self, audio_path, language_hint=None):
        normalized_hint = self._normalize_language(language_hint)
        segments, info = self.stt_model.transcribe(audio_path, language=normalized_hint, task="transcribe")
        text = " ".join([seg.text for seg in segments]).strip()
        detected_language = self._resolve_response_language(normalized_hint, getattr(info, "language", None))
        return text or "Could not understand", detected_language

    # ---------------- Chatbot (RAG query) ----------------
    def query_chatbot(self, question, target_language="en"):
        question_cleaned = clean_text(question)
        # Let RAG system handle errors internally - it has better error messages
        answer = self.rag.query(question_cleaned, target_language=target_language)
        emotion = "neutral"
        return answer, emotion

    # ---------------- TTS ----------------
    def tts(self, text, target_language="en"):
        client = Murf(api_key=self.murf_api_key)
        voice_id = self.voice_map.get(target_language, self.voice_map["en"])
        response = client.text_to_speech.generate(text=text, voice_id=voice_id)
        audio_url = response.audio_file
        
        local_file = OUTPUT_DIR / f"{uuid.uuid4()}.wav"
        r = requests.get(audio_url)
        with open(local_file, "wb") as f:
            f.write(r.content)
            
        return local_file



    # ---------------- Full pipeline ----------------
    def pipeline(self, audio_path, language_hint=None):
        question, detected_language = self.stt(audio_path, language_hint=language_hint)
        answer_language = detected_language or "en"
        answer, emotion = self.query_chatbot(question, target_language=answer_language)
        tts_file = self.tts(answer, target_language=answer_language)

        return {
            "question": question,
            "answer": answer,
            "language": answer_language,
            "audio_url": str(tts_file),
            "emotion": emotion
        }
