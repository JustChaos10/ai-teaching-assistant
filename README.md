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
│
├── backend/                 # Core backend modules
├── image detector/          # Image-based learning and detection games
├── asset/                   # Static assets (UI, media, etc.)
├── docs/                    # Documentation
├── indexes/                 # Index files for reference
├── animations/              # Animation assets
├── teachbot/                # Chatbot-related modules
│
├── game_manager.py          # Main game loop/manager
├── teacher_interface.py     # Teacher-facing interface
├── chatbot_logic.py         # Chatbot backend logic
├── teaching_prompts.py      # Teaching prompts and rules
├── module_executor.py       # Runs different modules
├── avatar_system.py         # Avatar system for engagement
├── py_app.py                # App runner
├── setup_api_keys.py        # Setup for API keys (⚠ don’t commit real keys)
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (⚠ keep private)
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
