# 🧠 AI Teaching Assistant

An **AI-powered teaching assistant** with interactive games, a 3D voice chatbot, image detection modules, and teacher-student interfaces — all built in Python and JavaScript.  
The goal is to make learning more engaging through **gamification** and **AI-driven interaction**.

---

## ✨ Features

- 🎮 **Gamified Learning**
  - Finger counting and gesture games  
  - Fruits vs. vegetables classifier  
  - Healthy vs. junk food detection  
  - Image-based puzzle activities  

- 🤖 **Chatbot & Avatar**
  - AI chatbot that listens and speaks  
  - Real-time lip-sync animation using **Rhubarb Lip Sync**  
  - Natural TTS (Text-to-Speech) responses  

- 👩‍🏫 **Teacher Interface**
  - Manage teaching prompts and sessions  
  - Launch activities directly from the GUI  

- 🖼️ **Image Detection**
  - Computer vision–based teaching modules  
  - Uses OpenCV for educational detection games  

- 🧩 **Modular Architecture**
  - Independent modules for Chatbot, Games, and CV tasks  
  - Extensible for adding new teaching tools  

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
├── image detector/                   # 🖼️ CV-based learning modules
│   ├── detector.py                   # Object detection logic
│   ├── finger_counting_game.py       # Hand gesture recognition
│   ├── fruits_vs_vegetables.py       # Food classification
│   ├── healthyVSjunk.py              # Food health categorization
│   ├── puzzle.py                     # Image puzzle mini-game
│   ├── images/, temp_images/         # Game assets
│   ├── puzzle_sprites/               # Sprite resources
│   └── requirements.txt              # CV dependencies
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
├── requirements.txt                  # Master dependency list
├── requirements_updated.txt          # Full merged dependency list
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
venv310\Scripts\activate
```

---

### 3️⃣ Install Dependencies
```bash
pip install -r requirements_updated.txt
```

---

## 🧩 Backend Setup (FastAPI)

1. Navigate to the backend folder:
   ```bash
   cd Capstone/backend
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

## 💻 Frontend Setup (React + React Three Fiber)

1. Open a **new terminal (make sure venv310 is activated again in this new terminal)**:
   ```bash
   cd Capstone/humanoid
   ```

2. Install Node.js:
   - Download from [Node.js LTS](https://nodejs.org/en/download/)
   - Check “Add to PATH” during setup.

3. Verify installation:
   ```bash
   node -v
   npm -v
   ```

4. Install frontend dependencies:
   ```bash
   npm install
   ```

5. Run the frontend:
   ```bash
   npm run dev
   ```

6. Open your browser at:
   ```bash
   http://localhost:5173/
   ```

---



---

## 🔐 Environment Variables

Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key
MURF_API_KEY=your_murf_api_key
```

---

## 🧠 How It Works

```
🎙️ Voice Input
   ↓
🧠 FastAPI backend (Whisper → LLM → TTS)
   ↓
🎧 Audio + Rhubarb JSON
   ↓
🧍 React Avatar (mouth animation syncs with phonemes)
```

---

## 🧰 Commands

| Task | Command |
|------|----------|
| Run backend | `uvicorn app:app --reload` |
| Run frontend | `npm run dev` |
| Install backend deps | `pip install -r requirements.txt` |
| Install frontend deps | `npm install` |
| Build frontend | `npm run build` |
| Clean npm cache | `npm cache clean --force` |

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| Voice Recognition | OpenAI Whisper |
| Text-to-Speech | Murf.ai |
| Lip Sync | Rhubarb Lip Sync |
| 3D Rendering | React Three Fiber |
| Backend | FastAPI |
| Frontend | React + Vite |
| Avatar Model | Ready Player Me |
| Animations | Mixamo FBX |

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
  ```

You can host:
- **Backend:** Render / Railway / AWS EC2  
- **Frontend:** Vercel / Netlify

---



---

## 📜 License

This project is licensed under the **MIT License**.  
See [LICENSE](LICENSE) for details.

---

> 🟢 *“Making education more interactive, one avatar at a time.”*
