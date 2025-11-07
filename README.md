# 🧠 AI Teaching Assistant

An **AI-powered teaching assistant** with interactive games, a 3D voice chatbot, and comprehensive teacher-student interfaces for Grade 1 learning — all built in Python and JavaScript.
The goal is to make learning more engaging through **gamification** and **AI-driven interaction**.

---

## ✨ Features

- 🎮 **Gamified Learning (AI Teaching Assistant)**
  - Finger counting and gesture games
  - Healthy vs. junk food detection
  - Image-based puzzle activities

- 🤖 **Chatbot & Avatar (AI Teaching Assistant)**
  - AI chatbot that listens and speaks
  - Real-time lip-sync animation using **Rhubarb Lip Sync**
  - Natural TTS (Text-to-Speech) responses

- 👩‍🏫 **Teacher Interface (AI Teaching Assistant)**
  - Manage teaching prompts and sessions
  - Launch activities directly from the GUI

- 📚 **BudgetBridge 2: Grade 1 Learning Platform**
  - Teachers add lectures (text) and get an AI summary.
  - Generate multiple-choice quizzes from a lecture with AI.
  - Students can take quizzes; scores are stored and retrievable.
  - Bright, playful interface optimized for young children.

- 🧩 **Modular Architecture**
  - Independent modules for Chatbot, Games, and the BudgetBridge 2 platform.
  - Extensible for adding new teaching tools.

---

## 📂 Project Structure

```
ai-teaching-assistant/
├── backend/                         # 🧠 FastAPI backend (STT → LLM → TTS → Rhubarb)
│   ├── app.py                        # FastAPI entry point
│   ├── teacher_chatbot_app.py        # Chatbot pipeline integration
│   ├── teacher_chatbot.py            # Core chatbot class
│   ├── rag_system.py                 # RAG (Retrieval-Augmented Generation)
│   ├── docs/                         # Teaching PDFs for RAG ingestion
│   ├── outputs/                      # Generated TTS audio + lip sync JSONs
│   ├── templates/test.html           # Upload test UI
│   └── requirements.txt              # Backend dependencies
│
├── humanoid/                         # 🧍 React + Three.js avatar frontend
│   ├── public/
│   │   ├── animations/               # FBX animations (Idle, Greeting, etc.)
│   │   ├── models/                   # Avatar GLB model
│   │   ├── audios/                   # Audio samples
│   │   └── textures/                 # Background textures
│   ├── src/
│   │   ├── components/
│   │   │   ├── Avatar.jsx            # Lip-sync & TTS logic
│   │   │   └── Experience.jsx        # Scene setup (lighting, environment)
│   │   ├── App.jsx                   # Main React app
│   │   └── main.jsx                  # Vite entry point
│   ├── vite.config.js                # Frontend config
│   └── package.json                  # Frontend dependencies
│
├── Games/                            # 🎮 Interactive learning modules
│   ├── create_game.py                # Game creation utility
│   ├── detector.py                   # Base detection logic
│   ├── fingers_counting_trails.py    # Finger counting game
│   ├── main.py                       # Main game launcher
│   ├── created_games/                # Assets for created games
│   ├── sounds/                       # Game sound assets
│   ├── templates/                    # Game templates
│   └── utils/                        # Utility functions for games
│
├── BudgetBridge 2/                   # 📚 Grade 1 Learning Platform
│   └── BudgetBridge 2/
│       ├── client/                   # React app (Vite)
│       │   ├── public/               # Static assets
│       │   └── src/                  # React source code
│       ├── server/                   # Express.js backend
│       │   ├── huggingface.ts        # AI calls and normalization
│       │   ├── index.ts              # Express app entry
│       │   ├── routes.ts             # REST endpoints
│       │   └── storage.ts            # Storage (in-memory or Mongo via Mongoose)
│       └── shared/                   # Shared types (Zod)
│           └── schema.ts             # Data models for lectures, quizzes, questions, submissions
│
├── asset/                            # ⚙️ (LFS) AI model weights (ignored in Git)
│   ├── DVAE.safetensors
│   ├── Decoder.safetensors
│   ├── Embed.safetensors
│   ├── Vocos.safetensors
│   └── gpt/model.safetensors
│
├── animations/                       # 🌀 GIF animations (idle/speaking/thinking)
│   ├── idle.gif
│   ├── speaking.gif
│   └── listening.gif
│
├── requirements.txt                  # Master Python dependency list
│
├── launch_teacher_interface.py       # Launch complete teaching interface
├── teacher_interface.py              # Teacher GUI
├── module_executor.py                # Module manager (games/chatbot/CV)
├── chatbot_logic.py                  # Dialogue management
├── setup_api_keys.py                 # Environment variable setup
├── quick_test.py                     # Quick STT → LLM → TTS test
│
└── LICENSE                           # MIT license
```

---
## ⚙️ Prerequisites

Make sure you have:

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/en/download/)
- [Git](https://git-scm.com/downloads/)
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync/releases)

> 💡 On Windows, install Rhubarb to:
> ```
> C:\tools\rhubarb\rhubarb.exe
> ```

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/JustChaos10/ai-teaching-assistant.git
cd ai-teaching-assistant
```

---

### 2️⃣ Create a Virtual Environment
```bash
python3.10 -m venv venv310
# On Linux/Mac
source venv310/bin/activate
# On Windows
virtualenv venv310\Scripts\activate
```

---

### 3️⃣ Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Install Rhubarb Lip SYNC

download https://github.com/DanielSWolf/rhubarb-lip-sync/releases
and save it in a location
add that location to backend\config.py file under RHUBARB_PATH
---

### 4️⃣ Backend Setup (AI Teaching Assistant - FastAPI)

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Run the FastAPI server:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

3. Wait for:
   ```bash
   Application startup complete
   ```
   ✅ Now your backend runs on:
   ```bash
   http://127.0.0.1:8000
   ```

---

### 5️⃣ Frontend Setup (AI Teaching Assistant - React + Three.js Avatar)

1. Open a **new terminal (make sure venv310 is activated again in this new terminal)**:
   ```bash
   cd humanoid
   cd r3f-lipsync-tutorial
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Run the frontend:
   ```bash
   npm run dev
   ```

4. Open your browser at:
   ```bash
   http://localhost:5173/
   ```

---

### 6️⃣ BudgetBridge 2 Setup (Grade 1 Learning Platform)

1. Open a **new terminal**:
   ```bash
   cd BudgetBridge 2/BudgetBridge 2
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Run the development server (Express + Vite):
   ```bash
   npm run dev
   ```

4. Open your browser at:
   ```bash
   http://localhost:5000
   ```

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following:
```bash
OPENAI_API_KEY=your_openai_api_key
MURF_API_KEY=your_murf_api_key
GROQ_API_KEY=your_groq_api_key
MONGODB_URI=your_mongodb_connection_string # Optional; if set, uses MongoDB via Mongoose
PORT=5000 # Optional; default for BudgetBridge 2 server
```

---

## 🧠 How It Works

The AI Teaching Assistant combines several modules:
- **Voice Input:** User's speech is captured.
- **FastAPI Backend:** Processes voice input using Whisper (STT), sends to LLM, generates TTS response.
- **Rhubarb Lip Sync:** Creates lip-sync data from TTS audio.
- **React Avatar:** Displays a 3D avatar with real-time lip-sync.
- **Interactive Games:** Python-based games for gamified learning.
- **BudgetBridge 2 Platform:** A separate full-stack application for lecture summarization and quiz generation using Groq API.

```
🎙️ Voice Input (AI Teaching Assistant)
   ↓
🧠 FastAPI backend (Whisper → LLM → TTS)
   ↓
🎧 Audio + Rhubarb JSON
   ↓
🧍 React Avatar (mouth animation syncs with phonemes)

📚 BudgetBridge 2 (Separate Flow)
   ↓
📝 Teacher Uploads Lecture Content
   ↓
🧠 Express.js Backend (Groq API for Summarization & Quiz Generation)
   ↓
📊 Student Takes Quiz & Views Results
```

---

## 🧰 Commands

| Task | Command |
|------|----------|
| Run AI Teaching Assistant Backend | `cd backend && uvicorn app:app --reload --port 8000` |
| Run AI Teaching Assistant Frontend | `cd humanoid && npm run dev` |
| Run BudgetBridge 2 Dev Server | `cd BudgetBridge 2/BudgetBridge 2 && npm run dev` |
| Install Python Dependencies | `pip install -r requirements.txt` |
| Install AI Teaching Assistant Frontend Deps | `cd humanoid && npm install` |
| Install BudgetBridge 2 Frontend Deps | `cd BudgetBridge 2/BudgetBridge 2 && npm install` |
| Build AI Teaching Assistant Frontend | `cd humanoid && npm run build` |
| Build BudgetBridge 2 Frontend | `cd BudgetBridge 2/BudgetBridge 2 && npm run build` |
| Clean npm cache | `npm cache clean --force` |

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| **AI Teaching Assistant** | |
| Voice Recognition | OpenAI Whisper |
| Text-to-Speech | Murf.ai |
| Lip Sync | Rhubarb Lip Sync |
| 3D Rendering | React Three Fiber |
| Backend | FastAPI |
| Frontend | React + Vite |
| Avatar Model | Ready Player Me |
| Animations | Mixamo FBX |
| Interactive Games | OpenCV |
| **BudgetBridge 2** | |
| Frontend | React (TypeScript), Wouter, TanStack Query, Shadcn UI, Tailwind CSS, Fredoka font |
| Backend | Express.js, Groq API, Mongoose (for MongoDB persistence) |
| Data Storage | In-memory (default) or MongoDB |

---

## 📦 Deployment Notes

- Do **not** commit large `.safetensors` model files to GitHub.
- Add to `.gitignore`:
  ```
  venv310/
  __pycache__/
  outputs/
  node_modules/
  asset/
  *.safetensors
  BudgetBridge 2/BudgetBridge 2/node_modules/
  BudgetBridge 2/BudgetBridge 2/dist/
  BudgetBridge 2/BudgetBridge 2/.local/
  BudgetBridge 2/BudgetBridge 2/.Rhistory
  BudgetBridge 2/BudgetBridge 2/vite.config.ts.*
  ```

You can host:
- **AI Teaching Assistant Backend:** Render / Railway / AWS EC2
- **AI Teaching Assistant Frontend:** Vercel / Netlify
- **BudgetBridge 2:** Replit Autoscale / Render / Vercel / Netlify

---

## 📜 License

This project is licensed under the **MIT License**.
See [LICENSE](LICENSE) for details.

---

> 🟢 *“Making education more interactive, one avatar at a time.”*