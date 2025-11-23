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
from config import OUTPUT_DIR, MURF_VOICE_EN, MURF_VOICE_TA, GROQ_API_KEY, IMAGES_DIR
from image_generator import ImageGenerator


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
        
        # ---------------- IMAGE GENERATOR ----------------
        self.image_generator = None
        print(f"[TeacherChatbot] Checking image generator initialization...")
        print(f"[TeacherChatbot] GROQ_API_KEY present: {bool(GROQ_API_KEY)}")
        
        if GROQ_API_KEY:
            try:
                self.image_generator = ImageGenerator(
                    groq_api_key=GROQ_API_KEY,
                    output_dir=IMAGES_DIR
                )
                print("[TeacherChatbot] ✅ Image generator initialized (Pollinations.ai - Free, No Auth)")
            except Exception as e:
                print(f"[TeacherChatbot] ❌ Image generator initialization failed: {e}")
        else:
            print("[TeacherChatbot] ❌ Image generator disabled (missing GROQ_API_KEY)")

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
        print(f"\n{'='*60}")
        print(f"[Pipeline] Starting pipeline...")
        
        question, detected_language = self.stt(audio_path, language_hint=language_hint)
        print(f"[Pipeline] Question: {question}")
        
        answer_language = detected_language or "en"
        answer, emotion = self.query_chatbot(question, target_language=answer_language)
        print(f"[Pipeline] Answer: {answer[:100]}...")
        
        tts_file = self.tts(answer, target_language=answer_language)
        print(f"[Pipeline] TTS generated: {tts_file}")

        # ---------------- Generate images if enabled ----------------
        image_urls = []
        print(f"[Pipeline] Image generator available: {self.image_generator is not None}")
        
        if self.image_generator:
            try:
                print(f"[Pipeline] 🎨 Starting image generation...")
                print(f"[Pipeline] Answer text for analysis: '{answer}'")
                
                images = self.image_generator.generate_images_for_teaching(answer)
                print(f"[Pipeline] Generated {len(images)} images")
                
                # Convert file paths to URLs for frontend
                for img in images:
                    # Path is already relative (e.g., static/generated_images/xxx.png)
                    # Just ensure forward slashes and add leading /
                    path_str = str(img["path"]).replace("\\", "/")
                    if not path_str.startswith("/"):
                        path_str = "/" + path_str
                    
                    image_urls.append({
                        "url": path_str,
                        "description": img["description"],
                        "step": img["step"],
                        "start_time": img.get("start_time", 0),
                        "duration": img.get("duration", 3.0)
                    })
                    print(f"[Pipeline] Image {img['step']}: {path_str} (start: {img.get('start_time', 0)}s, duration: {img.get('duration', 3)}s)")
                
                print(f"[Pipeline] ✅ Successfully generated {len(image_urls)} image URLs")
            except Exception as e:
                print(f"[Pipeline] ❌ Error generating images: {e}")
                import traceback
                traceback.print_exc()
                # Continue without images
        else:
            print(f"[Pipeline] ⚠️ Image generator not initialized, skipping images")

        print(f"{'='*60}\n")

        return {
            "question": question,
            "answer": answer,
            "language": answer_language,
            "audio_url": str(tts_file),
            "emotion": emotion,
            "images": image_urls  # New field with image URLs
        }