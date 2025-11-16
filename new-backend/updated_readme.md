# 🧠 AI Teaching Assistant

An **AI-powered teaching assistant** with interactive games, a 2D Live2D voice chatbot, and comprehensive teacher-student interfaces for Grade 1 learning — all built in Python and JavaScript.
The goal is to make learning more engaging through **gamification** and **AI-driven interaction**.

---

## ✨ Features

- 🎮 **Gamified Learning (AI Teaching Assistant)**
  - Finger counting and gesture games
  - Healthy vs. junk food detection
  - Image-based puzzle activities
  - Launch games directly from the web interface

- 🤖 **Chatbot & Avatar (AI Teaching Assistant)**
  - AI chatbot that listens and speaks
  - **Live2D 2D character** with real-time audio-driven lip-sync
  - Natural TTS (Text-to-Speech) responses
  - Q&A mode, Lecture mode, and Games launcher
  - Processing indicator during audio generation

- 👩‍🏫 **Teacher Interface (AI Teaching Assistant)**
  - Manage teaching prompts and sessions
  - Launch activities directly from the GUI

- 📚 **BudgetBridge 3: Grade 1 Learning Platform**
  - Teachers add lectures (text) and get an AI summary.
  - Generate multiple-choice quizzes from a lecture with AI.
  - Students can take quizzes; scores are stored and retrievable.
  - Bright, playful interface optimized for young children.

- 🧩 **Modular Architecture**
  - Independent modules for Chatbot, Games, and the BudgetBridge 3 platform.
  - Extensible for adding new teaching tools.

---

## 📂 Project Structure

```
ai-teaching-assistant/
├── backend/                         # 🧠 FastAPI backend (STT → LLM → TTS) - This is the original backend.
│   ├── app.py                        # FastAPI entry point with /launch-games endpoint
│   ├── teacher_chatbot_app.py        # Chatbot pipeline integration
│   ├── teacher_chatbot.py            # Core chatbot class
│   ├── rag_system.py                 # RAG (Retrieval-Augmented Generation)
│   ├── docs/                         # Teaching PDFs for RAG ingestion
│   ├── outputs/                      # Generated TTS audio files
│   ├── templates/test.html           # Upload test UI
│   └── requirements.txt              # Backend dependencies
├── new-backend/                     # 🧠 FastAPI backend (STT → LLM → TTS) - This is the newer, updated version of the backend.
│   ├── app.py                        # FastAPI entry point with /launch-games endpoint
│   ├── teacher_chatbot_app.py        # Chatbot pipeline integration
│   ├── teacher_chatbot.py            # Core chatbot class
│   ├── rag_system.py                 # RAG (Retrieval-Augmented Generation)
│   ├── docs/                         # Teaching PDFs for RAG ingestion
│   ├── outputs/                      # Generated TTS audio files
│   ├── templates/test.html           # Upload test UI
│   └── requirements.txt              # Backend dependencies
│
├── humanoid/                         # 🤖 2D Live2D avatar frontend
│   ├── 2d mode integ/                # **ACTIVE** - Live2D integration (Dependencies are included within this folder)
│   │   ├── public/
│   │   │   └── Resources/            # Live2D Hiyori model files
│   │   │       └── Hiyori/
│   │   │           ├── Hiyori.model3.json
│   │   │           ├── Hiyori.moc3
│   │   │           ├── *.png (textures)
│   │   │           ├── *.motion3.json (animations)
│   │   │           └── *.physics3.json
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   └── Avatar.jsx        # Live2D rendering & audio-driven lip-sync
│   │   │   ├── vendor/               # Cubism SDK for Web 5-r.4
│   │   │   ├── App.jsx               # Main React app with Q&A/Lectures/Games tabs
│   │   │   └── main.jsx              # Vite entry point
│   │   ├── vite.config.js            # Frontend config
│   │   └── package.json              # Frontend dependencies
│   │
│   └── r3f-lipsync-tutorial/         # Legacy 3D avatar (requires Rhubarb Lip Sync for lip-sync functionality)
│       └── ...
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
├── BudgetBridge 2/                   # 📚 Grade 1 Learning Platform (This is the older version)
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
├── BudgetBridge 3/                   # 📚 Grade 1 Learning Platform (This is the newer version)
│   └── BudgetBridge 3/
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
├── animations/                       # 🖼️ GIF animations (idle/speaking/thinking)
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

## 🛠️ Prerequisites

Make sure you have:

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/en/download/)
- [Git](https://git-scm.com/downloads/)
- **Live2D Cubism SDK for Web** (included in `humanoid/2d mode integ/src/vendor/`)
- **Rhubarb Lip Sync** (required for `humanoid/r3f-lipsync-tutorial/` for lip-sync functionality)

> 💡 **Note:** The `humanoid/2d mode integ` uses Web Audio API for audio-driven lip sync and does not require Rhubarb Lip Sync.

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

---

### 4️⃣ Backend Setup (AI Teaching Assistant - FastAPI)

1. Navigate to the backend folder (choose `backend` for the original or `new-backend` for the updated version):
   ```bash
   cd new-backend
   # or cd backend
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

### 5️⃣ Frontend Setup (AI Teaching Assistant - Live2D Avatar)

1. Open a **new terminal**:
   ```bash
   cd humanoid
   cd "2d mode integ"
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

> 💡 The Live2D Cubism SDK is already included in `src/vendor/`. The Hiyori model files are in `public/Resources/Hiyori/`. Both should be included when deploying.

---

### 6️⃣ BudgetBridge 3 Setup (Grade 1 Learning Platform)

1. Open a **new terminal**:
   ```bash
   cd BudgetBridge 3/BudgetBridge 3
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

## 🔑 Environment Variables

Create a `.env` file in the project root with the following:
```bash
OPENAI_API_KEY=your_openai_api_key
MURF_API_KEY=your_murf_api_key
GROQ_API_KEY=your_groq_api_key
MONGODB_URI=your_mongodb_connection_string # Optional; if set, uses MongoDB via Mongoose
PORT=5000 # Optional; default for BudgetBridge 3 server
```

---

## 🧠 How It Works

The AI Teaching Assistant combines several modules:
- **Voice Input:** User's speech is captured via browser microphone.
- **FastAPI Backend:** Processes voice input using Whisper (STT), sends to LLM, generates TTS response.
- **Live2D Avatar:** Displays a 2D character with real-time audio-driven lip-sync using Web Audio API.
- **Interactive Games:** Python-based games for gamified learning, launched from web interface.
- **BudgetBridge 3 Platform:** A separate full-stack application for lecture summarization and quiz generation using Groq API.

```
🎤 Voice Input (AI Teaching Assistant)
   ↓
🧠 FastAPI backend (Whisper → LLM → TTS)
   ↓
🔊 Audio (WAV file)
   ↓
👁️ Live2D Avatar (Web Audio API analyzes audio → ParamMouthOpenY lip-sync)

🎮 Games Launcher
   ↓
🖱️ Click "Launch Games" button
   ↓
💻 Backend launches Games/main.py (Tkinter GUI)

📚 BudgetBridge 3 (Separate Flow)
   ↓
📝 Teacher Uploads Lecture Content
   ↓
🧠 Express.js Backend (Groq API for Summarization & Quiz Generation)
   ↓
📊 Student Takes Quiz & Views Results
```

---

## 📜 Commands

| Task | Command |
|------|----------|
| Run AI Teaching Assistant Backend | `cd new-backend && uvicorn app:app --reload --port 8000` |
| Run AI Teaching Assistant Frontend | `cd "humanoid/2d mode integ" && npm run dev` |
| Run BudgetBridge 3 Dev Server | `cd "BudgetBridge 3/BudgetBridge 3" && npm run dev` |
| Install Python Dependencies | `pip install -r requirements.txt` |
| Install AI Teaching Assistant Frontend Deps | `cd "humanoid/2d mode integ" && npm install` |
| Install BudgetBridge 3 Frontend Deps | `cd "BudgetBridge 3/BudgetBridge 3" && npm install` |
| Build AI Teaching Assistant Frontend | `cd "humanoid/2d mode integ" && npm run build` |
| Build BudgetBridge 3 Frontend | `cd "BudgetBridge 3/BudgetBridge 3" && npm run build` |
| Clean npm cache | `npm cache clean --force` |

---

## ⚙️ Tech Stack

| Component | Technology |
|------------|-------------|
| **AI Teaching Assistant** | |
| Voice Recognition | OpenAI Whisper |
| Text-to-Speech | Murf.ai |
| Lip Sync | Web Audio API (frequency analysis) |
| 2D Rendering | Live2D Cubism SDK for Web 5-r.4 |
| Backend | FastAPI |
| Frontend | React + Vite + PixiJS |
| Avatar Model | Live2D Hiyori (Cubism model) |
| Animations | CubismBreath, CubismPhysics, CubismPose |
| Interactive Games | OpenCV, Tkinter |
| **BudgetBridge 3** | |
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
  BudgetBridge 3/BudgetBridge 3/node_modules/
  BudgetBridge 3/BudgetBridge 3/dist/
  BudgetBridge 3/BudgetBridge 3/.local/
  BudgetBridge 3/BudgetBridge 3/.Rhistory
  BudgetBridge 3/BudgetBridge 3/vite.config.ts.*
  ```

You can host:
- **AI Teaching Assistant Backend:** Render / Railway / AWS EC2
- **AI Teaching Assistant Frontend:** Vercel / Netlify (build the `humanoid/2d mode integ` folder)
- **BudgetBridge 3:** Replit Autoscale / Render / Vercel / Netlify

> 💡 **Live2D Note:** The Cubism SDK files are in `humanoid/2d mode integ/src/vendor/`. The Hiyori model is in `public/Resources/Hiyori/`. Both should be included when deploying.

---

## 📄 License

This project is licensed under the **MIT License**.
See [LICENSE](LICENSE) for details.

---

> 🧡 *“Making education more interactive, one avatar at a time.”*