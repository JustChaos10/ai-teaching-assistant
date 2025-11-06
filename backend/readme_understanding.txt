# AI Teaching Assistant Backend Explained

This document outlines the architecture and functionality of the AI Teaching Assistant's backend system and how the frontend interacts with it.

## Backend Architecture

The backend is a sophisticated system composed of several key components, primarily built with Python and FastAPI.

### 1. Core AI and Logic (Python)

*   **Web Server (`app.py`):** The main entry point is a `FastAPI` web server. It exposes several API endpoints that the frontend application communicates with. Its primary roles are:
    *   Handling audio uploads from the user for questions.
    *   Serving the generated audio responses.
    *   Proxying lecture and quiz-related requests to a separate Node.js service.

*   **Chatbot Orchestrator (`teacher_chatbot_app.py`):** The `TeacherChatbot` class is the heart of the AI. It orchestrates the entire process when a user asks a question:
    1.  **Speech-to-Text:** It uses a `Whisper` model to transcribe the user's spoken question from an audio file into text.
    2.  **Question Answering:** It sends the transcribed question to the RAG system to get an answer.
    3.  **Text-to-Speech:** It uses the `murf.ai` service to convert the text answer into high-quality speech.
    4.  **Lip Sync Generation:** It uses a tool called `Rhubarb` to generate phoneme data from the audio, which is used to animate an avatar's lips to match the spoken words.

*   **Retrieval-Augmented Generation (`rag_system.py`):** The `RAGSystem` class is the "brain" that finds and generates answers.
    *   **Document Ingestion:** It can read and extract text from various document formats like PDF, DOCX, and PPTX located in the `/docs` folder.
    *   **Vectorization:** It uses `Sentence-Transformers` to convert the text from these documents into numerical representations (embeddings) and stores them in a `FAISS` vector index. This allows for very fast and efficient searching.
    *   **Information Retrieval:** When a question is asked, it searches the FAISS index to find the most relevant pieces of information from the ingested documents.
    *   **Answer Generation:** It then uses a powerful Large Language Model (`llama-3.1-8b-instant` via the `Groq` API) to generate a natural, educational, and age-appropriate answer. The retrieved documents are provided to the model as context, ensuring the answers are based on the course material. It's specifically prompted to act as a patient and encouraging teacher for young students.

*   **Command-Line Interface (`teacher_chatbot.py`):** This file provides a way for a developer to interact with and test the RAG system directly from the command line, including a voice chat mode.

### 2. Lecture & Quiz Management (Node.js - External)

*   The Python backend communicates with a separate Node.js application running on `localhost:5000`. This Node.js service is responsible for handling the creation, storage, and retrieval of lecture materials and quizzes.

---

## Frontend Interaction (React + Vite)

The React + Vite frontend, located in the `humanoid` sibling folder, interacts with the Python FastAPI backend (running on `http://localhost:8000`) through standard HTTP requests.

### 1. Q&A Mode (Audio Input)

*   The frontend captures audio from the user's microphone.
*   It sends this audio as a `multipart/form-data` POST request to the backend's `/ask` endpoint.
*   The backend responds with a JSON object containing the transcribed question, the text answer, a URL to the generated audio response, and phoneme data for animation.

### 2. Serving Audio Files

*   After receiving an `audio_url` (e.g., `/audio/some-uuid.wav`) from the `/ask` or `/speak` endpoints, the frontend constructs the full URL (e.g., `http://localhost:8000/audio/some-uuid.wav`).
*   It then makes a GET request to this URL to retrieve and play the audio file.

### 3. Text-to-Speech (TTS) for Summaries/Answers

*   When the frontend needs to convert text (e.g., a lecture summary) into speech, it sends a JSON POST request to the `/speak` endpoint with the text to be spoken.
*   The backend returns a JSON object with the audio URL and phoneme data, similar to the Q&A mode.

### 4. Lecture Mode (Proxied to Node.js)

*   For operations like listing, getting, or creating lectures, and generating quizzes, the frontend makes requests to the FastAPI backend's `/lectures` or `/quizzes/generate` endpoints.
*   FastAPI acts as a proxy, forwarding these requests to the Node.js API (`http://localhost:5000/api`) and returning the response to the frontend.

The `CORSMiddleware` configured in `app.py` ensures that the frontend can safely make these cross-origin requests to the backend during development.
