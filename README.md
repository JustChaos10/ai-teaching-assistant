# AI Teaching Assistant

An **AI-powered teaching assistant** with interactive games, chatbot prompts, image detection modules, and teacher-student interfaces — all built in Python. The goal is to make learning engaging through gamification and AI-driven interactions.

---

## ✨ Features

- 🎮 **Gamified Learning**
  - Finger counting games
  - Fruits vs. vegetables classification
  - Healthy vs. junk food activities
  - Puzzle and sprite-based exercises

- 🤖 **Chatbot & Prompts**
  - Chatbot logic with custom teaching prompts
  - Avatar system for more engaging conversations

- 👩‍🏫 **Teacher Interface**
  - Launch and control teacher-facing UI
  - Manage prompts, sessions, and activities

- 🖼 **Image Detection**
  - Simple computer vision modules for interactive lessons
  - Image datasets and detectors for practice tasks

- 🛠 **Modular Architecture**
  - Backend with multiple Python modules
  - Extendable design for adding new games or teaching modules

---

## 📂 Project Structure

```bash
ai-teaching-assistant/
├── .env.example                        # Example environment variable file
├── .gitignore                          # Ignored files and directories
├── .gitattributes                      # Git LFS and line-ending settings
├── README.md                           # Main project documentation
├── LICENSE                             # License file
│
├── backend/                            # 🧩 Core backend system (FastAPI + RAG)
│   ├── app.py                          # FastAPI server with /ask and /audio endpoints
│   ├── teacher_chatbot.py              # Main TeacherChatbot class (STT → LLM → TTS → Rhubarb)
│   ├── teacher_chatbot_app.py          # Backend entrypoint (integrates chatbot pipeline)
│   ├── rag_system.py                   # Retrieval-Augmented Generation system (RAG)
│   ├── requirements.txt                # Backend dependencies
│   ├── templates/
│   │   └── test.html                   # Simple frontend for testing API uploads
│   ├── docs/                           # Educational content (ingested into RAG)
│   │   ├── aejm101.pdf … aemr1ps.pdf   # Teaching material PDFs
│   ├── indexes/faiss_index/            # Vector database (FAISS index)
│   │   ├── index.faiss
│   │   └── index.pkl
│   └── outputs/                        # Generated TTS audio + Rhubarb phoneme JSONs
│
├── humanoid/                           # 🧍 Frontend humanoid avatar system (React Three Fiber)
│   └── r3f-lipsync-tutorial/           # React + Three.js + ReadyPlayerMe + Rhubarb
│       ├── public/
│       │   ├── animations/             # FBX animation clips (Idle, Greeting, Speaking, etc.)
│       │   ├── audios/                 # Example test audios
│       │   ├── models/                 # Avatar GLB model
│       │   └── textures/               # Background images
│       ├── src/
│       │   ├── components/
│       │   │   ├── Avatar.jsx          # Avatar component — handles lip sync & expressions
│       │   │   └── Experience.jsx      # Scene setup (camera, lighting, animations)
│       │   ├── App.jsx                 # Main React app component
│       │   └── main.jsx                # Entry point for Vite app
│       ├── vite.config.js              # Vite configuration
│       └── package.json                # Frontend dependencies
│
├── image detector/                     # 🖼️ Interactive learning mini-games (CV-based)
│   ├── detector.py                     # Core object detection logic
│   ├── finger_counting_game.py         # Hand gesture recognition (counting fingers)
│   ├── fruits_vs_vegetables.py         # Food classification game
│   ├── healthyVSjunk.py                # Healthy vs junk food detection
│   ├── puzzle.py                       # Simple image puzzle game
│   ├── images/, temp_images/           # Game assets and temp storage
│   ├── puzzle_sprites/                 # Sprite assets for puzzles
│   └── requirements.txt                # Requirements for image detector subsystem
│
├── animations/                         # 🌀 GIF animations for idle/listening/speaking states
│   ├── idle.gif
│   ├── listening.gif
│   ├── speaking.gif
│   ├── thinking.gif
│   └── index.html                      # Test page for displaying animations
│
├── asset/                              # ⚙️ (LFS) Model weights (not pushed to GitHub)
│   ├── DVAE.safetensors
│   ├── Decoder.safetensors
│   ├── Embed.safetensors
│   ├── Vocos.safetensors
│   └── gpt/model.safetensors
│
├── requirements.txt                    # Master dependency list (for deployment)
├── requirements_updated.txt            # Expanded dependencies (merged envs)
│
├── launch_teacher_interface.py         # Main launcher for full AI assistant
├── teacher_interface.py                # GUI interface for chatbot
├── module_executor.py                  # Runtime module manager (voice, CV, chatbot)
├── chatbot_logic.py                    # Chat reasoning and dialogue logic
├── setup_api_keys.py                   # Utility for setting environment variables
├── quick_test.py                       # Script for testing API flow (STT → LLM → TTS)
│
├── FIXED_SPEECH_ISSUES.md              # Documentation of fixed issues in TTS/STT
├── ISSUES_FIXED_SUMMARY.md             # Summary of fixes and known issues
├── README_TEACHER_SYSTEM.md            # Backend system documentation
├── SPEECH_RECOGNITION_GUIDE.md         # Guide for speech pipeline setup
├── TEST_RESULTS.md                     # Logs and evaluation results
└── runnotes.txt                        # Developer notes and run instructions

```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/ai-teaching-assistant.git
cd ai-teaching-assistant
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate    # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the teacher interface
```bash
python launch_teacher_interface.py
```

---

## ⚙️ Requirements

- Python 3.9+
- Libraries listed in `requirements.txt` (e.g., OpenAI, Gradio, Torch, etc. depending on your modules)
- (Optional) Webcam for image-based activities

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following (example):

```bash
OPENAI_API_KEY=your_api_key_here
```

---

## 🛡️ License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributions

Contributions, issues, and feature requests are welcome!  
Feel free to fork this repo and open a pull request.

---

## 📌 Notes

- This project is modular — add new games by creating a Python module and linking it in `game_manager.py`.

---

## 🎯 Roadmap

- Add more AI-driven activities
- Improve computer vision modules
- Expand teacher dashboard with analytics
- Support for multilingual prompts
