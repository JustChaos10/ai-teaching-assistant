# 🧠 AI Teaching Assistant

An **AI-powered teaching assistant** combining interactive educational games, a 2D Live2D voice-enabled chatbot, and a comprehensive Grade 1 learning platform. Built with Python (FastAPI), React, and Live2D Cubism SDK, this system delivers an engaging, gamified learning experience for young students.

---

## ✨ Key Features

### 🤖 AI Voice Chatbot with Live2D Avatar
- **Real-time voice interaction:** Speak to the AI and receive natural voice responses
- **Live2D 2D character:** Animated Hiyori character with realistic physics and breathing
- **Audio-driven lip-sync:** Mouth movements synchronized with speech using Web Audio API
- **Multiple modes:** Q&A, Lecture delivery, and Games launcher
- **Visual feedback:** Processing indicator during AI response generation

### 🎮 Interactive Learning Games
- **Gesture-based games:** Finger counting recognition using MediaPipe
- **Computer vision activities:** Healthy vs. junk food classification
- **Puzzle games:** Image-based cognitive challenges
- **Easy launch:** Start games directly from the web interface
- **Child-friendly UI:** Bright, colorful Tkinter interface designed for Grade 1

### 📚 BudgetBridge Learning Platform
- **AI-powered lecture summarization:** Teachers input content, AI generates summaries
- **Automatic quiz generation:** Create multiple-choice quizzes from lecture content
- **Student assessment:** Quiz-taking interface with score tracking
- **Data persistence:** Optional MongoDB integration for storing results
- **Groq API integration:** Fast, efficient AI processing

### 🔧 Technical Highlights
- **Modular architecture:** Independent, extensible components
- **RAG system:** Retrieval-Augmented Generation for contextual responses
- **Multiple backend options:** Choose between original or updated backend
- **Web Audio API:** Real-time audio analysis for lip synchronization
- **No external dependencies:** Live2D SDK and models included in repository

---

## 📂 Project Architecture

```
ai-teaching-assistant/
│
├── 🧠 BACKEND SERVICES (Python FastAPI)
│   ├── backend/                      # Original backend implementation
│   │   ├── app.py                    # FastAPI server with STT→LLM→TTS pipeline
│   │   ├── teacher_chatbot.py        # Core chatbot logic with RAG
│   │   ├── teacher_chatbot_app.py    # Chatbot integration layer
│   │   ├── rag_system.py             # Document retrieval system (FAISS + embeddings)
│   │   ├── config.py                 # API keys and configuration
│   │   ├── docs/                     # Teaching materials for RAG ingestion
│   │   ├── outputs/                  # Generated audio files (WAV)
│   │   └── requirements.txt          # Backend-specific dependencies
│   │
│   └── new-backend/                  # Updated backend (recommended)
│       ├── app.py                    # Enhanced FastAPI with /launch-games endpoint
│       ├── teacher_chatbot.py        # Improved chatbot with better error handling
│       ├── teacher_chatbot_app.py    # Updated integration layer
│       ├── rag_system.py             # Optimized RAG implementation
│       ├── config.py                 # Configuration management
│       ├── docs/                     # Teaching PDFs
│       ├── outputs/                  # Audio output directory
│       └── requirements.txt          # Dependencies
│
├── 🎨 FRONTEND (React + Live2D)
│   └── humanoid/
│       ├── 2d mode integ/            # ✅ ACTIVE - Live2D implementation
│       │   ├── public/
│       │   │   └── Resources/Hiyori/ # Live2D model files
│       │   │       ├── Hiyori.model3.json  # Model configuration
│       │   │       ├── Hiyori.moc3         # Model data
│       │   │       ├── *.png               # Textures
│       │   │       ├── *.motion3.json      # Animation data
│       │   │       └── *.physics3.json     # Physics configuration
│       │   ├── src/
│       │   │   ├── components/
│       │   │   │   └── Avatar.jsx    # Live2D renderer + lip-sync engine
│       │   │   ├── vendor/           # Cubism SDK for Web 5-r.4
│       │   │   │   └── Framework/    # Live2D framework modules
│       │   │   ├── modelConfig.js    # Model selection (Haru/Hiyori/Mao/Mark/Natori/Rice/Wanko)
│       │   │   ├── App.jsx           # Main UI with tabs (Q&A/Lectures/Games)
│       │   │   └── main.jsx          # Vite entry point
│       │   ├── package.json          # Frontend dependencies
│       │   └── vite.config.js        # Build configuration
│       │
│       └── r3f-lipsync-tutorial/     # Legacy 3D avatar (not actively used)
│
├── 🎮 GAMES SYSTEM (Python + OpenCV)
│   └── Games/
│       ├── main.py                   # Tkinter game launcher GUI
│       ├── create_game.py            # Game creation utility
│       ├── detector.py               # Color detection base class
│       ├── fingers_counting_trails.py # MediaPipe hand tracking
│       ├── templates/                # Game templates
│       │   ├── base_game.py          # Abstract base game class
│       │   ├── binary_choice.py      # Two-option games (healthy/junk food)
│       │   ├── numeric_input.py      # Finger counting games
│       │   └── puzzle.py             # Image puzzle games
│       ├── utils/
│       │   └── image_processing.py   # OpenCV utilities
│       ├── created_games/            # User-created game assets
│       └── sounds/                   # Audio effects
│
├── 📚 BUDGETBRIDGE PLATFORM (Node.js + React)
│   ├── BudgetBridge 2/BudgetBridge 2/  # Original version
│   │   ├── client/                   # React frontend (Vite)
│   │   │   ├── src/                  # React components
│   │   │   └── public/               # Static assets
│   │   ├── server/                   # Express.js backend
│   │   │   ├── index.ts              # Server entry point
│   │   │   ├── routes.ts             # API endpoints
│   │   │   ├── huggingface.ts        # AI integration
│   │   │   └── storage.ts            # Data persistence layer
│   │   ├── shared/
│   │   │   └── schema.ts             # Zod schemas (lectures/quizzes/submissions)
│   │   └── package.json
│   │
│   └── BudgetBridge 2/BudgetBridge 3/  # ✅ Updated version (recommended)
│       └── [Same structure as BudgetBridge 2]
│
├── 📦 CONFIGURATION & ASSETS
│   ├── requirements.txt              # 🎯 Master Python dependencies (ALL packages)
│   ├── .env                          # Environment variables (API keys)
│   ├── .gitignore                    # Git exclusions
│   ├── setup_api_keys.py             # Environment setup utility
│   └── teaching_prompts.py           # Prompt templates
│
└── 📄 DOCUMENTATION
    ├── README.md                     # This file
    ├── LICENSE                       # MIT License
    └── *.md                          # Additional documentation
```

---

## 🛠️ Prerequisites

Ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.10+ | Backend services, Games |
| **Node.js** | 18+ | Frontend, BudgetBridge platform |
| **npm** | 8+ | Package management |
| **Git** | Latest | Version control |

**Included in Repository:**
- ✅ Live2D Cubism SDK for Web 5-r.4 (`humanoid/2d mode integ/src/vendor/`)
- ✅ Hiyori model files (`public/Resources/Hiyori/`)
- ✅ All required JavaScript libraries

**NOT Required:**
- ❌ Rhubarb Lip Sync (old system used phonemes; new system uses Web Audio API)

---

## 🚀 Quick Start Guide

### 📥 Step 1: Clone Repository

```bash
git clone https://github.com/JustChaos10/ai-teaching-assistant.git
cd ai-teaching-assistant
```

### 🐍 Step 2: Python Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install ALL Python dependencies from master requirements.txt
pip install -r requirements.txt
```

> 💡 **Note:** The master `requirements.txt` includes dependencies for backend, games, and all Python components. Individual `requirements.txt` files in subdirectories are redundant but kept for reference.

### 🔑 Step 3: Configure API Keys

Create a `.env` file in the project root:

```env
# Required for AI Teaching Assistant
OPENAI_API_KEY=sk-...              # OpenAI API for Whisper STT and GPT
MURF_API_KEY=...                   # Murf.ai for Text-to-Speech
GROQ_API_KEY=...                   # Groq API for BudgetBridge

# Optional - Database
MONGODB_URI=mongodb://...          # MongoDB connection (optional, defaults to in-memory)
PORT=5000                          # BudgetBridge server port (optional, default: 5000)
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Murf.ai: https://murf.ai/
- Groq: https://console.groq.com/

Or use the setup script:
```bash
python setup_api_keys.py
```

---

## 🎯 Running the System

### 🧠 Backend Server (Choose One)

**Option A: Updated Backend (Recommended)**
```bash
cd new-backend
uvicorn app:app --reload --port 8000
```

**Option B: Original Backend**
```bash
cd backend
uvicorn app:app --reload --port 8000
```

**Verify Backend is Running:**
- Server URL: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Wait for: `Application startup complete`

**Key Endpoints:**
- `POST /chat` - Process voice/text input
- `GET /audio/{filename}` - Retrieve generated audio
- `POST /lecture` - Generate lecture audio
- `POST /launch-games` - Launch Games GUI

---

### 🎨 Frontend (Live2D Avatar)

**In a NEW terminal:**

```bash
cd "humanoid/2d mode integ"

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Access Application:**
- URL: `http://localhost:5173`
- Features: Q&A tab, Lectures tab, Games tab
- Avatar: Live2D Hiyori character with lip-sync

**Changing the Avatar Model:**
Edit `src/modelConfig.js`:
```javascript
export const modelConfig = {
  modelName: 'Hiyori',  // Change to: Haru, Mao, Mark, Natori, Rice, or Wanko
  // ...
};
```

Available models must be in `public/Resources/{ModelName}/`

---

### 🎮 Games System

**Method 1: Launch from Web Interface**
1. Open frontend (`http://localhost:5173`)
2. Click "Games" tab
3. Click "Launch Games" button
4. Games GUI window opens (Tkinter)

**Method 2: Direct Launch**
```bash
cd Games
python main.py
```

**Available Games:**
- **Finger Counting:** Uses MediaPipe hand tracking
- **Healthy vs Junk:** Color-based food classification  
- **Puzzles:** Image-based cognitive challenges

---

### 📚 BudgetBridge Platform

**In a NEW terminal:**

```bash
# Use BudgetBridge 3 (recommended)
cd "BudgetBridge 2/BudgetBridge 3"

# Install dependencies (first time only)
npm install

# Start server (Express + Vite)
npm run dev
```

**Access Platform:**
- URL: `http://localhost:5000`

**Features:**
- Teacher: Add lectures → Get AI summary → Generate quiz
- Student: Take quiz → Submit answers → View scores
- Admin: Manage lectures, quizzes, and submissions

---

## 🧠 System Architecture & Data Flow

### Voice Interaction Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Browser Microphone    │
        │  (MediaRecorder API)   │
        └──────────┬─────────────┘
                   │ WAV audio
                   ▼
        ┌────────────────────────┐
        │   FastAPI Backend      │
        │   POST /chat           │
        └──────────┬─────────────┘
                   │
                   ▼
        ┌────────────────────────┐
        │  Whisper STT           │
        │  (OpenAI API)          │
        └──────────┬─────────────┘
                   │ Text
                   ▼
        ┌────────────────────────┐
        │  RAG System            │
        │  (FAISS + Embeddings)  │
        └──────────┬─────────────┘
                   │ Context
                   ▼
        ┌────────────────────────┐
        │  LLM (GPT-4)           │
        │  Generate Response     │
        └──────────┬─────────────┘
                   │ Response text
                   ▼
        ┌────────────────────────┐
        │  Murf.ai TTS           │
        │  Generate Audio        │
        └──────────┬─────────────┘
                   │ WAV file
                   ▼
        ┌────────────────────────┐
        │  Save to outputs/      │
        │  Return filename       │
        └──────────┬─────────────┘
                   │
                   ▼
        ┌────────────────────────┐
        │  Frontend Audio Fetch  │
        │  GET /audio/{filename} │
        └──────────┬─────────────┘
                   │
                   ▼
        ┌────────────────────────┐
        │  Web Audio API         │
        │  AnalyserNode          │
        └──────────┬─────────────┘
                   │ Frequency data
                   ▼
        ┌────────────────────────┐
        │  Live2D Lip-Sync       │
        │  ParamMouthOpenY       │
        └────────────────────────┘
```

### Live2D Rendering Pipeline

```javascript
// Avatar.jsx - Simplified flow
1. Load Live2D model (Hiyori.model3.json)
2. Initialize Cubism Framework
3. Create PixiJS canvas
4. Set up animation loop:
   - Update breath animation (CubismBreath)
   - Update physics (CubismPhysics)  
   - Apply pose (CubismPose)
   - Analyze audio frequency
   - Set mouth parameter: ParamMouthOpenY = volume
   - Render frame
```

### Games Launch Flow

```
Frontend (Games Tab)
    ↓ Click "Launch Games"
    ↓ POST /launch-games
Backend (app.py)
    ↓ subprocess.Popen([python, "Games/main.py"])
    ↓ CREATE_NO_WINDOW flag
Games GUI (Tkinter)
    ↓ Display game selection
    ↓ User selects game
    ↓ Launch game module
Game Module (OpenCV window)
    ↓ Camera feed + game logic
    ↓ Hand tracking / color detection
    ↓ Score tracking + feedback
```

---

## 📋 Complete Command Reference

### Backend Commands

| Task | Command | Port |
|------|---------|------|
| Start updated backend | `cd new-backend && uvicorn app:app --reload --port 8000` | 8000 |
| Start original backend | `cd backend && uvicorn app:app --reload --port 8000` | 8000 |
| View API docs | Open `http://127.0.0.1:8000/docs` | - |
| Test endpoint | `curl http://127.0.0.1:8000/` | - |

### Frontend Commands

| Task | Command | Port |
|------|---------|------|
| Install dependencies | `cd "humanoid/2d mode integ" && npm install` | - |
| Start dev server | `npm run dev` | 5173 |
| Build for production | `npm run build` | - |
| Preview production build | `npm run preview` | 4173 |
| Clean cache | `npm cache clean --force` | - |

### BudgetBridge Commands

| Task | Command | Port |
|------|---------|------|
| Install dependencies | `cd "BudgetBridge 2/BudgetBridge 3" && npm install` | - |
| Start dev server | `npm run dev` | 5000 |
| Build for production | `npm run build` | - |
| Start production | `npm start` | 5000 |

### Games Commands

| Task | Command |
|------|---------|
| Launch from web | Click "Games" tab → "Launch Games" button |
| Direct launch | `cd Games && python main.py` |
| Create new game | `python create_game.py` |

### Python Environment

| Task | Command |
|------|---------|
| Install all dependencies | `pip install -r requirements.txt` |
| Update packages | `pip install --upgrade -r requirements.txt` |
| List installed | `pip list` |
| Export current | `pip freeze > requirements-freeze.txt` |

---

## 🔧 Tech Stack Details

### Backend (Python)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | REST API server, async support |
| **Voice Recognition** | OpenAI Whisper | Speech-to-text conversion |
| **Language Model** | GPT-4 (OpenAI) | Natural language understanding |
| **Text-to-Speech** | Murf.ai | High-quality voice synthesis |
| **Vector Database** | FAISS | Fast similarity search for RAG |
| **Embeddings** | Sentence Transformers | Text embeddings for retrieval |
| **Document Processing** | PyPDF, docx2txt, python-pptx | Extract text from files |
| **Computer Vision** | OpenCV, MediaPipe | Hand tracking, image processing |
| **GUI Framework** | Tkinter | Games launcher interface |

**Key Libraries:**
```
fastapi, uvicorn      # Web server
langchain-groq        # LLM integration
faiss-cpu             # Vector search
sentence-transformers # Embeddings
opencv-python         # Computer vision
mediapipe             # Hand tracking
pygame                # Game audio/rendering
torch, transformers   # ML models
```

### Frontend (JavaScript/React)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | React 19 | UI components and state management |
| **Build Tool** | Vite 7.2 | Fast development and bundling |
| **2D Rendering** | PixiJS 7.3 | Hardware-accelerated canvas rendering |
| **Character System** | Live2D Cubism SDK 5-r.4 | 2D model rendering and animation |
| **Audio Processing** | Web Audio API | Real-time audio frequency analysis |
| **Model Format** | `.model3.json`, `.moc3` | Live2D model files |

**Character Animation Modules:**
- `CubismFramework`: Core SDK initialization
- `CubismUserModel`: Model loading and management
- `CubismRenderer_WebGL`: GPU-accelerated rendering
- `CubismBreath`: Breathing animation
- `CubismPhysics`: Hair/clothing physics
- `CubismPose`: Pose blending and transitions

**Lip-Sync Implementation:**
```javascript
// Web Audio API pipeline
AudioContext → MediaElementSource → AnalyserNode → getByteFrequencyData()
    ↓
Calculate volume average (0-255)
    ↓
Normalize to 0.0-1.0 range
    ↓
Set Live2D parameter: model.setParameterValueById(mouthId, volume)
```

### BudgetBridge (Full-Stack TypeScript)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React + TypeScript | Type-safe UI components |
| **Routing** | Wouter | Lightweight client-side routing |
| **State** | TanStack Query | Server state management and caching |
| **Styling** | Tailwind CSS + Shadcn UI | Utility-first CSS + component library |
| **Backend** | Express.js | REST API server |
| **AI** | Groq API | Fast LLM inference (Llama 3) |
| **Database** | MongoDB (optional) / In-memory | Data persistence |
| **Validation** | Zod | Runtime type checking |

**Data Models:**
- `Lecture`: Text content, AI summary, metadata
- `Quiz`: Questions, correct answers, lecture reference
- `Question`: Text, options, correct answer
- `Submission`: Student answers, score, timestamp

---

## 🎨 Customization Guide

### Changing the Avatar

**1. Select Different Model:**
Edit `humanoid/2d mode integ/src/modelConfig.js`:
```javascript
export const modelConfig = {
  modelName: 'Mao',  // Options: Haru, Hiyori, Mao, Mark, Natori, Rice, Wanko
  models: {
    Mao: {
      scale: 0.8,      // Adjust size
      position: { x: 0.0, y: 0.1 }  // Adjust position
    }
  }
};
```

**2. Add Custom Model:**
1. Place model files in `public/Resources/YourModel/`
2. Required files:
   - `YourModel.model3.json` (model configuration)
   - `YourModel.moc3` (model data)
   - Textures (`.png` files)
   - Optional: `.motion3.json`, `.physics3.json`
3. Update `modelConfig.js` with new model entry

### Modifying Lip-Sync Sensitivity

Edit `humanoid/2d mode integ/src/components/Avatar.jsx`:
```javascript
// Find the lip-sync calculation
const averageVolume = dataArray.reduce((a, b) => a + b) / bufferLength;
const normalizedVolume = Math.min(averageVolume / 255, 1.0);

// Adjust sensitivity (multiply by factor > 1 for more movement)
const lipSyncValue = normalizedVolume * 1.5;  // Increase sensitivity
```

### Adding New Games

1. **Create Game Class** in `Games/templates/`:
```python
from templates.base_game import BaseGame

class MyNewGame(BaseGame):
    def __init__(self, config):
        super().__init__(config)
        self.title = "My New Game"
    
    def generate_question(self):
        # Game logic here
        pass
    
    def check_answer(self, user_input):
        # Validation logic
        pass
```

2. **Register in main.py:**
```python
from templates.my_new_game import MyNewGame

# Add to game launcher UI
```

3. **Create Game Assets:**
- Place images in `created_games/MyNewGame/`
- Add sounds in `sounds/`

---

## 🚀 Deployment

### Backend Deployment

**Render / Railway / AWS:**
1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn new-backend.app:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (API keys)
5. Deploy

**Docker:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "new-backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Deployment

**Vercel / Netlify:**
1. Connect repository
2. Build command: `npm run build`
3. Build directory: `dist`
4. Root directory: `humanoid/2d mode integ`
5. Add environment variable: `VITE_API_URL=https://your-backend.com`

**Important:** Update API URL in `App.jsx`:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### BudgetBridge Deployment

**Replit / Render:**
1. Build command: `npm install && npm run build`
2. Start command: `npm start`
3. Add environment variables (GROQ_API_KEY, MONGODB_URI)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** API keys not found
**Solution:**
```bash
# Create .env file with:
OPENAI_API_KEY=...
MURF_API_KEY=...
GROQ_API_KEY=...
```

**Problem:** Port 8000 already in use
**Solution:**
```bash
# Use different port
uvicorn app:app --reload --port 8001
```

### Frontend Issues

**Problem:** `Cannot find module 'react'`
**Solution:**
```bash
cd "humanoid/2d mode integ"
npm install
```

**Problem:** Live2D model not loading
**Solution:**
1. Check console for errors
2. Verify model files exist in `public/Resources/Hiyori/`
3. Check `modelConfig.js` model name matches folder name

**Problem:** Audio not playing
**Solution:**
1. Check backend is running (`http://127.0.0.1:8000`)
2. Open browser console for errors
3. Check CORS settings in backend `app.py`

### Games Issues

**Problem:** Games window doesn't appear
**Solution:**
- Check backend logs for subprocess errors
- Run `python Games/main.py` directly to see errors
- Ensure Tkinter is installed: `pip install tk`

**Problem:** Camera not working
**Solution:**
```bash
# Check camera permissions
# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

---

## 📊 Performance Optimization

### Backend
- **Use caching:** Cache RAG embeddings and model responses
- **Async processing:** Leverage FastAPI's async capabilities
- **Connection pooling:** Reuse HTTP connections for API calls

### Frontend
- **Code splitting:** Lazy load Avatar component
- **Audio preloading:** Preload next audio response
- **Optimize textures:** Compress Live2D textures (PNG → WebP)

### Games
- **Reduce frame rate:** Lower camera FPS if laggy
- **Optimize detection:** Use smaller input images for MediaPipe

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 AI Teaching Assistant Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

See [LICENSE](LICENSE) for full details.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

- **Issues:** https://github.com/JustChaos10/ai-teaching-assistant/issues
- **Documentation:** See `*.md` files in repository
- **API Docs:** `http://127.0.0.1:8000/docs` (when backend running)

---

## 🎯 Roadmap

- [ ] Add more Live2D character models
- [ ] Implement voice emotion detection
- [ ] Multi-language support (i18n)
- [ ] Progressive Web App (PWA) support
- [ ] Teacher dashboard with analytics
- [ ] Mobile app versions (React Native)
- [ ] Multiplayer games mode
- [ ] Integration with Google Classroom

---

> 🧡 **"Making education more interactive, one avatar at a time."**

Built with ❤️ for Grade 1 learners everywhere.

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
├── backend/                         # 🧠 FastAPI backend (STT → LLM → TTS)
│   ├── app.py                        # FastAPI entry point with /launch-games endpoint
│   ├── teacher_chatbot_app.py        # Chatbot pipeline integration
│   ├── teacher_chatbot.py            # Core chatbot class
│   ├── rag_system.py                 # RAG (Retrieval-Augmented Generation)
│   ├── docs/                         # Teaching PDFs for RAG ingestion
│   ├── outputs/                      # Generated TTS audio files
│   ├── templates/test.html           # Upload test UI
│   └── requirements.txt              # Backend dependencies
│
├── humanoid/                         # 🧍 2D Live2D avatar frontend
│   ├── 2d mode integ/                # **ACTIVE** - Live2D integration
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
│   └── r3f-lipsync-tutorial/         # Legacy 3D avatar (not currently used)
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
- **Live2D Cubism SDK for Web** (included in `humanoid/2d mode integ/src/vendor/`)

> 💡 **Note:** Rhubarb Lip Sync is no longer required. The new 2D Live2D avatar uses Web Audio API for audio-driven lip sync.

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

> 💡 The Live2D Cubism SDK is already included in `src/vendor/`. The Hiyori model files are in `public/Resources/Hiyori/`.

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
- **Voice Input:** User's speech is captured via browser microphone.
- **FastAPI Backend:** Processes voice input using Whisper (STT), sends to LLM, generates TTS response.
- **Live2D Avatar:** Displays a 2D character with real-time audio-driven lip-sync using Web Audio API.
- **Interactive Games:** Python-based games for gamified learning, launched from web interface.
- **BudgetBridge 2 Platform:** A separate full-stack application for lecture summarization and quiz generation using Groq API.

```
🎙️ Voice Input (AI Teaching Assistant)
   ↓
🧠 FastAPI backend (Whisper → LLM → TTS)
   ↓
🎧 Audio (WAV file)
   ↓
🧍 Live2D Avatar (Web Audio API analyzes audio → ParamMouthOpenY lip-sync)

🎮 Games Launcher
   ↓
🖱️ Click "Launch Games" button
   ↓
🐍 Backend launches Games/main.py (Tkinter GUI)

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
| Run AI Teaching Assistant Frontend | `cd "humanoid/2d mode integ" && npm run dev` |
| Run BudgetBridge 2 Dev Server | `cd "BudgetBridge 2/BudgetBridge 2" && npm run dev` |
| Install Python Dependencies | `pip install -r requirements.txt` |
| Install AI Teaching Assistant Frontend Deps | `cd "humanoid/2d mode integ" && npm install` |
| Install BudgetBridge 2 Frontend Deps | `cd "BudgetBridge 2/BudgetBridge 2" && npm install` |
| Build AI Teaching Assistant Frontend | `cd "humanoid/2d mode integ" && npm run build` |
| Build BudgetBridge 2 Frontend | `cd "BudgetBridge 2/BudgetBridge 2" && npm run build` |
| Clean npm cache | `npm cache clean --force` |

---

## 🧩 Tech Stack

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
- **AI Teaching Assistant Frontend:** Vercel / Netlify (build the `humanoid/2d mode integ` folder)
- **BudgetBridge 2:** Replit Autoscale / Render / Vercel / Netlify

> 💡 **Live2D Note:** The Cubism SDK files are in `humanoid/2d mode integ/src/vendor/`. The Hiyori model is in `public/Resources/Hiyori/`. Both should be included when deploying.

---

## 📜 License

This project is licensed under the **MIT License**.
See [LICENSE](LICENSE) for details.

---

> 🟢 *“Making education more interactive, one avatar at a time.”*