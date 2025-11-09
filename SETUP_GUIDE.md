# 🎓 AI Teaching Assistant - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Setup (FastAPI)](#backend-setup-fastapi)
3. [Frontend Setup (React with Live2D)](#frontend-setup-react-with-live2d)
4. [Live2D Model Setup](#live2d-model-setup)
5. [BudgetBridge 2 Setup](#budgetbridge-2-setup)
6. [Games Module Setup](#games-module-setup)
7. [Running All Services](#running-all-services)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

Make sure you have the following installed:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/en/download/)
- **Git** - [Download](https://git-scm.com/downloads/)
- **Rhubarb Lip Sync** - [Download](https://github.com/DanielSWolf/rhubarb-lip-sync/releases)

### System Requirements
- **OS:** Windows, macOS, or Linux
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 2GB free space

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/JustChaos10/ai-teaching-assistant.git
cd ai-teaching-assistant
```

---

## 🐍 Backend Setup (FastAPI)

### Step 1: Create Python Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv venv310

# Activate virtual environment
# On Linux/Mac:
source venv310/bin/activate

# On Windows:
venv310\Scripts\activate
```

### Step 2: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure API Keys

Create a `.env` file in the project root:

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
MURF_API_KEY=your_murf_api_key_here
GROQ_API_KEY=your_groq_api_key_here
MONGODB_URI=mongodb://localhost:27017/budgetbridge  # Optional
PORT=5000
```

Or use the setup script:

```bash
python setup_api_keys.py
```

### Step 4: Configure Rhubarb Lip Sync

1. Download Rhubarb from https://github.com/DanielSWolf/rhubarb-lip-sync/releases
2. Extract to a location (e.g., `C:\tools\rhubarb\` on Windows)
3. Update `backend/config.py`:

```python
# backend/config.py
RHUBARB_PATH = "C:\\tools\\rhubarb\\rhubarb.exe"  # Windows
# or
RHUBARB_PATH = "/usr/local/bin/rhubarb"  # Linux/Mac
```

### Step 5: Run the Backend Server

```bash
cd backend
uvicorn app:app --reload --port 8000
```

✅ **Backend is now running at:** `http://127.0.0.1:8000`

---

## ⚛️ Frontend Setup (React with Live2D)

### Step 1: Navigate to Frontend Directory

```bash
cd humanoid/r3f-lipsync-tutorial
```

### Step 2: Install Node.js Dependencies

```bash
npm install
```

**Dependencies installed:**
- `react` & `react-dom` - UI framework
- `pixi.js` - 2D rendering engine
- `@pixi/live2d-display` - Live2D model rendering
- `vite` - Build tool & dev server

### Step 3: Run the Frontend Development Server

```bash
npm run dev
```

✅ **Frontend is now running at:** `http://localhost:5173`

---

## 🎭 Live2D Model Setup

### Why Live2D?

This project now uses **Live2D Cubism** instead of React Three Fiber for more expressive 2D character animations with better lip-sync capabilities.

### Step 1: Download Shizuka Model

**Option A: Official Live2D Sample**

1. Visit https://www.live2d.com/en/download/sample-data/
2. Download the **"Shizuku"** sample model
3. Extract the ZIP file

**Option B: From Open-LLM-VTuber**

```bash
# Clone the reference repository
git clone https://github.com/Open-LLM-VTuber/Open-LLM-VTuber.git
cd Open-LLM-VTuber/live2d-models
# Copy shizuku folder to your project
```

### Step 2: Place Model Files

Copy the extracted files to:

```
ai-teaching-assistant/
└── humanoid/
    └── r3f-lipsync-tutorial/
        └── public/
            └── live2d-models/
                └── shizuku/
                    ├── shizuku.model.json    # Main config
                    ├── shizuku.moc           # Model data
                    ├── *.png                 # Textures
                    ├── motions/              # Animations (optional)
                    └── expressions/          # Expressions (optional)
```

### Step 3: Verify Model Path

The Live2D Avatar component expects the model at:
```
/live2d-models/shizuku/shizuku.model.json
```

If your model structure is different, update `src/components/Live2DAvatar.jsx`:

```javascript
const model = await Live2DModel.from(
  "/live2d-models/shizuku/shizuku.model.json",
  { autoInteract: false }
);
```

### Live2D Licensing Notice

⚠️ **Important:** The Shizuka model is provided by Live2D Inc. under their **Free Material License Agreement**.

- ✅ Free for personal/educational use
- ✅ Free for non-commercial projects
- ❌ Commercial use requires proper licensing

Read the full license: https://www.live2d.com/en/terms/live2d-free-material-license-agreement/

---

## 📚 BudgetBridge 2 Setup

BudgetBridge 2 is the Grade 1 learning platform with lecture summarization and quiz generation.

### Step 1: Navigate to BudgetBridge Directory

```bash
cd "BudgetBridge 2/BudgetBridge 2"
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Run Development Server

```bash
npm run dev
```

✅ **BudgetBridge 2 is now running at:** `http://localhost:5000`

### Features:
- 📝 Teachers upload lecture content → AI generates summaries
- 🧠 AI-powered quiz generation using Groq API
- 📊 Students take quizzes and view scores
- 🎨 Bright, child-friendly interface

---

## 🎮 Games Module Setup

Interactive Python-based educational games using OpenCV.

### Available Games:
- 🖐 **Finger Counting** - Computer vision-based counting
- 🥗 **Healthy vs Junk Food** - Image classification game
- 🧩 **Puzzle Games** - Interactive puzzle solving

### Running Games Standalone:

```bash
cd Games
python main.py
```

### Running Games from Frontend:

Click the **"Games"** tab in the frontend UI and press **"Launch Games"** button.

---

## 🏃 Running All Services

To run the complete AI Teaching Assistant, you need **3 terminals**:

### Terminal 1: Backend (FastAPI)

```bash
cd backend
source ../venv310/bin/activate  # On Windows: ..\venv310\Scripts\activate
uvicorn app:app --reload --port 8000
```

### Terminal 2: Frontend (React + Live2D)

```bash
cd humanoid/r3f-lipsync-tutorial
npm run dev
```

### Terminal 3: BudgetBridge 2 (Optional)

```bash
cd "BudgetBridge 2/BudgetBridge 2"
npm run dev
```

### Service URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | http://127.0.0.1:8000 | FastAPI server (STT, LLM, TTS) |
| **Frontend** | http://localhost:5173 | React UI with Live2D avatar |
| **BudgetBridge 2** | http://localhost:5000 | Learning platform |

---

## 🧰 Useful Commands

### Backend

| Task | Command |
|------|---------|
| Run backend | `cd backend && uvicorn app:app --reload --port 8000` |
| Test API | `curl http://127.0.0.1:8000/` |
| Install packages | `pip install -r requirements.txt` |

### Frontend

| Task | Command |
|------|---------|
| Install deps | `cd humanoid/r3f-lipsync-tutorial && npm install` |
| Run dev server | `npm run dev` |
| Build for production | `npm run build` |
| Preview build | `npm run preview` |

### BudgetBridge 2

| Task | Command |
|------|---------|
| Install deps | `cd "BudgetBridge 2/BudgetBridge 2" && npm install` |
| Run dev server | `npm run dev` |
| Build | `npm run build` |

### Games

| Task | Command |
|------|---------|
| Launch games | `cd Games && python main.py` |
| Create new game | `python create_game.py` |

---

## 🔍 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv310/bin/activate  # Linux/Mac
venv310\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem:** Rhubarb lip sync not working

**Solution:**
1. Download Rhubarb: https://github.com/DanielSWolf/rhubarb-lip-sync/releases
2. Update `backend/config.py` with correct path
3. Test Rhubarb: `rhubarb --version`

---

### Frontend Issues

**Problem:** Live2D model not loading

**Solution:**
1. Check browser console for errors (F12)
2. Verify model files are in `/public/live2d-models/shizuku/`
3. Check that `shizuku.model.json` exists
4. Ensure all `.png` textures are present

**Problem:** `npm run dev` fails

**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm run dev
```

**Problem:** CORS errors in browser console

**Solution:**
- Backend CORS is already configured for `*`
- If still having issues, check if backend is running on port 8000

---

### Live2D Specific Issues

**Problem:** Model appears but doesn't animate

**Solution:**
1. Check that audio is playing (check browser console)
2. Verify phoneme data is being received from backend
3. Check Live2D parameter names in `Live2DAvatar.jsx`

**Problem:** Model is too large/small

**Solution:**

Edit `src/components/Live2DAvatar.jsx`:

```javascript
// Adjust scale multiplier (default is 0.8 and 0.9)
const scaleX = (app.screen.width * 1.0) / model.width;  // Increase for larger
const scaleY = (app.screen.height * 1.0) / model.height;
```

---

### BudgetBridge 2 Issues

**Problem:** Groq API errors

**Solution:**
- Ensure `GROQ_API_KEY` is set in `.env`
- Check API quota: https://console.groq.com/

**Problem:** MongoDB connection failed

**Solution:**
- BudgetBridge 2 uses in-memory storage by default
- MongoDB is optional - only needed for persistence
- If using MongoDB, ensure `MONGODB_URI` is correct in `.env`

---

## 📦 Tech Stack Summary

### Backend
- **FastAPI** - REST API server
- **OpenAI Whisper** - Speech-to-Text
- **Murf.ai** - Text-to-Speech
- **Rhubarb Lip Sync** - Phoneme generation

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **PIXI.js** - 2D rendering engine
- **@pixi/live2d-display** - Live2D Cubism integration

### BudgetBridge 2
- **Express.js** - Node.js backend
- **Groq API** - AI summarization & quiz generation
- **React** - Frontend UI
- **Mongoose** - MongoDB ORM (optional)

### Games
- **Python** - Core language
- **OpenCV** - Computer vision
- **Tkinter** - GUI framework

---

## 🎯 What Changed from Previous Version?

### Before (React Three Fiber)
- Used 3D GLB models from Ready Player Me
- React Three Fiber + Three.js for 3D rendering
- FBX animations for character movement
- Heavier bundle size (~2MB+)

### Now (Live2D)
- Uses 2D Live2D Cubism models (Shizuka)
- PIXI.js + @pixi/live2d-display
- Native Live2D parameter-based animations
- Lighter bundle size (~800KB)
- Better lip-sync and facial expressions

### Benefits:
✅ More expressive character animations
✅ Better lip-sync accuracy
✅ Smaller file sizes
✅ Easier to customize expressions
✅ Established VTuber technology

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

**Live2D Assets:** Separately licensed under the Live2D Free Material License Agreement.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📞 Support

Having issues?
1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing issues: https://github.com/JustChaos10/ai-teaching-assistant/issues
3. Open a new issue with detailed logs

---

> 🟢 *"Making education more interactive, one Live2D avatar at a time."*
