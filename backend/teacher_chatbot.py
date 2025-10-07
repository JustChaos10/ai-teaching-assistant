import os
from rag_system import RAGSystem
from dotenv import load_dotenv
import pygame
import requests

load_dotenv()
import torch
import numpy as np
from scipy.io.wavfile import write as write_wav
import subprocess
import re
import unicodedata
import inflect
from RealtimeSTT import AudioToTextRecorder

p = inflect.engine()
from murf import Murf



# ----------------- SYMBOL MAP -----------------
SYMBOL_MAP = {
    '+': 'plus',
    '-': 'minus',
    '*': 'times',
    '/': 'divided by',
    '=': 'equals',
    '%': 'percent',
    '>': 'greater than',
    '<': 'less than',
    '&': 'and',
    '@': 'at',
    '#': 'number',
    '$': 'dollar',
    '^': 'caret',
    '√': 'square root',
}

# ----------------- CLEAN TEXT -----------------
def clean_text(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    for symbol, word in SYMBOL_MAP.items():
        text = text.replace(symbol, f' {word} ')

    def replace_digits(match):
        num = int(match.group(0))
        return p.number_to_words(num)
    text = re.sub(r'\b\d+\b', replace_digits, text)

    text = re.sub(r'[^\w\s.,\'-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return "Let's try again."
    return text

# ----------------- TTS SETUP -----------------
# from ChatTTS import Chat
# chattts = ChatTTS.Chat()
# chattts.load(compile=False)
# torch.manual_seed(1330)
# spk_id = chattts.sample_random_speaker()

# params_infer_code = ChatTTS.Chat.InferCodeParams(
#     spk_emb=spk_id,
#     temperature=0.7,
#     top_P=0.9,
#     top_K=30,
# )
# params_refine_text = ChatTTS.Chat.RefineTextParams()

def speak_with_chattts(text1):


    client = Murf(api_key="ap2_5f202fde-8bb8-41c2-a021-81c8757d64b9")

    response = client.text_to_speech.generate(
        text=text1,
        voice_id="en-US-natalie"
    )



    # Download audio
    audio_url = response.audio_file
    local_file = "output.wav"
    r = requests.get(audio_url)
    with open(local_file, "wb") as f:
        f.write(r.content)

    # Play audio
    pygame.mixer.init()
    pygame.mixer.music.load(local_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# ----------------- DOC INGEST -----------------
def auto_ingest_docs(rag, docs_folder="./docs"):
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
        return
    supported_exts = {".pdf", ".docx", ".pptx", ".txt"}
    files = [f for f in os.listdir(docs_folder) if os.path.isfile(os.path.join(docs_folder, f))]
    if not files:
        return
    for file_name in files:
        ext = os.path.splitext(file_name)[1].lower()
        if ext in supported_exts:
            file_path = os.path.join(docs_folder, file_name)
            try:
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                rag.ingest_file(file_name, file_bytes)
            except Exception:
                pass

# ----------------- TEXT CHAT -----------------
def chat_mode(rag):
    print("\n🎓 **Text Chat Mode**")
    while True:
        try:
            question = input("\n📝 You: ").strip()
            if question.lower() == 'quit':
                break
            elif question.lower() == 'clear':
                rag.conversation_history = []
                rag.current_subject = None
                print("🧹 Conversation cleared!")
                continue
            elif not question:
                continue
            print("🤔 Thinking...")
            answer = rag.query(question)
            print(f"👩‍🏫 Teacher: {answer}")
            speak_with_chattts(answer)
        except KeyboardInterrupt:
            return

# ----------------- VOICE CHAT -----------------
def chat_mode_voice(rag):
    print("\n🎤 **Voice Chat Mode (Wake word: 'jarvis')**")
    print("Say 'jarvis' to wake me, then ask your question!")
    print("Say 'quit' to exit voice mode.")
    print("-" * 60)

    latest_text = {"value": ""}

    def on_wakeword():
        print("\n👂 Wake word detected! I'm listening...")

    recorder = AudioToTextRecorder(
        wakeword_backend="pvporcupine",
        wake_words="jarvis",
        wake_words_sensitivity=0.6,
        on_wakeword_detected=on_wakeword,
        on_vad_start=lambda: print("(Speech detected...)"),
        on_vad_stop=lambda: print("(Speech ended.)"),
    )
    recorder.start()

    try:
        while True:
            # Get latest transcription from STT
            recorder.text(lambda text: latest_text.update({"value": text}))

            if latest_text["value"]:
                question = latest_text["value"].strip().lower()
                latest_text["value"] = ""

                if not question:
                    continue
                elif question == "quit":
                    print("👋 Exiting voice mode.")
                    break
                elif question == "clear":
                    rag.conversation_history = []
                    rag.current_subject = None
                    print("🧹 Conversation cleared!")
                    continue
                elif question in ["menu", "back"]:
                    return

                print(f"🗣 You said: {question}")
                print("🤔 Thinking...")
                answer = rag.query(question)
                print(f"👩‍🏫 Teacher: {answer}")
                speak_with_chattts(answer)
    except KeyboardInterrupt:
        print("\n\n👋 Voice mode interrupted.")
    finally:
        recorder.stop()


# ----------------- MENU -----------------
def print_menu():
    print("\n" + "="*50)
    print("🎓 **Smart Learning Teacher for Grades 1-2** 🎓")
    print("="*50)
    print("1. 📁 Add a document")
    print("2. ❓ Ask a quick question")
    print("3. 💬 Start learning chat (text)")
    print("4. 🎤 Start learning chat (voice)")
    print("5. 🗑️ Clear all data")
    print("6. 👋 Exit")
    print("-" * 50)

# ----------------- MAIN -----------------
def main():
    print("🚀 Starting your Learning Teacher...")
    try:
        rag = RAGSystem()
        auto_ingest_docs(rag)
        print("🎉 Ready to help you learn!")

        while True:
            print_menu()
            choice = input("Choose an option (1-6): ").strip()
            if choice == "1":
                file_path = input("📂 Path to document: ").strip()
                if not os.path.isfile(file_path):
                    print("❌ File not found.")
                    continue
                try:
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    file_name = os.path.basename(file_path)
                    msg = rag.ingest_file(file_name, file_bytes)
                    print(f"✅ {msg}")
                except Exception as e:
                    print(f"❌ Error adding document: {e}")
            elif choice == "2":
                question = input("❓ Question: ").strip()
                if not question:
                    continue
                try:
                    print("🤔 Thinking...")
                    answer = rag.query(question)
                    print(f"👩‍🏫 Teacher: {answer}")
                except Exception as e:
                    print(f"❌ Error: {e}")
            elif choice == "3":
                chat_mode(rag)
            elif choice == "4":
                chat_mode_voice(rag)
            elif choice == "5":
                confirm = input("⚠️ Clear all data? (y/n): ").strip().lower()
                if confirm == "y":
                    msg = rag.clear_all_data()
                    print(f"✅ {msg}")
                else:
                    print("❌ Cancelled.")
            elif choice == "6":
                print("👋 Goodbye! Keep learning!")
                break
            else:
                print("❌ Invalid choice.")
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
