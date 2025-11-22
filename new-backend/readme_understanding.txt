# AI Teaching Assistant Backend Explained

This document outlines the architecture and functionality of the AI Teaching Assistant's backend system and how the frontend interacts with it.

## Backend Architecture

The backend is a sophisticated system composed of several key components, primarily built with Python and FastAPI.

### 1. Core AI and Logic (Python)

*   **Configuration (`config.py`):** This file centralizes all key configuration variables, making them easily modifiable without altering core application logic. It defines:
    *   `RHUBARB_PATH`: The path to the Rhubarb lip-sync executable.
    *   `MURF_API_KEY`: The API key for the Murf AI text-to-speech service (loaded from environment variables).
    *   `GROQ_API_KEY`: The API key for Groq LLM service (loaded from environment variables).
    *   `HUGGINGFACE_API_KEY`: The API key for Hugging Face image generation (loaded from environment variables).
    *   `LECTURE_API_BASE`: The base URL for the external Node.js lecture API.
    *   `OUTPUT_DIR`: The directory where generated audio and phoneme files are stored.
    *   `IMAGES_DIR`: The directory where generated educational images are stored (static/generated_images/).

*   **Web Server (`app.py`):** The main entry point is a `FastAPI` web server. It exposes several API endpoints that the frontend application communicates with. Its primary roles are:
    *   Handling audio uploads from the user for questions.
    *   Serving the generated audio responses.
    *   Serving static image files from the `static/generated_images/` directory.
    *   Proxying lecture and quiz-related requests to a separate Node.js service.
    *   It imports `MURF_API_KEY`, `LECTURE_API_BASE`, and `OUTPUT_DIR` from `config.py`.

*   **Chatbot Orchestrator (`teacher_chatbot_app.py`):** The `TeacherChatbot` class orchestrates the entire process when a user asks a question:
    1.  **Speech-to-Text:** Uses a `Whisper` model to transcribe the user's spoken question from an audio file into text.
    2.  **Question Answering:** Sends the transcribed question to the RAG system to get an answer.
    3.  **Image Generation:** Analyzes the teaching content and generates synchronized educational images:
        *   Uses Groq's `llama-3.3-70b-versatile` LLM to analyze the answer, count words, estimate speaking time (2.5 words/second), and generate image prompts with calculated durations.
        *   Uses Hugging Face's `FLUX.1-schnell` model to generate images from the prompts.
        *   Calculates sequential timing (start_time, end_time) for each image to synchronize with audio narration.
        *   Returns image metadata: [{url, description, step, start_time, duration}].
    4.  **Text-to-Speech:** Uses the `murf.ai` service to convert the text answer into high-quality speech.
    5.  **Lip Sync Generation:** Uses `Rhubarb` to generate phoneme data from the audio for avatar lip animation.
    *   It imports `RHUBARB_PATH`, `OUTPUT_DIR`, `GROQ_API_KEY`, and `HUGGINGFACE_API_KEY` from `config.py`.
    *   Initializes `ImageGenerator` with both Groq and Hugging Face API keys for the image generation pipeline.

*   **Image Generator (`image_generator.py`):** The `ImageGenerator` class handles AI-powered educational image generation with LLM-calculated timing:
    1.  **Content Analysis:** Uses Groq LLM to analyze teaching content, count words, and estimate speaking duration.
    2.  **Prompt Generation:** LLM divides content into segments and creates detailed image prompts with calculated durations.
    3.  **Image Synthesis:** Uses Hugging Face FLUX Schnell to generate PNG images from prompts.
    4.  **Timing Calculation:** Assigns sequential start_time to each image based on LLM-calculated durations (e.g., 0s, 2.5s, 5s).
    5.  **Storage:** Saves images to `static/generated_images/` with UUID filenames.

*   **Command-Line Interface (`teacher_chatbot.py`):** This file provides a way for a developer to interact with and test the RAG system directly from the command line, including a voice chat mode.

### 2. Lecture & Quiz Management (Node.js - External)

*   The Python backend communicates with a separate Node.js application running on `localhost:5000`. This Node.js service is responsible for handling the creation, storage, and retrieval of lecture materials and quizzes.

---

## Frontend Interaction (React + Vite)

The React + Vite frontend, located in the `humanoid/2d mode integ` folder, interacts with the Python FastAPI backend (running on `http://localhost:8000`) through standard HTTP requests.

### 1. Q&A Mode (Audio Input)

*   The frontend captures audio from the user's microphone.
*   It sends this audio as a `multipart/form-data` POST request to the backend's `/ask` endpoint.
*   The backend responds with a JSON object containing:
    *   `question`: The transcribed question text
    *   `answer`: The text answer from the RAG system
    *   `audio_url`: URL to the generated audio response (e.g., `/audio/some-uuid.wav`)
    *   `phonemes`: Phoneme data for lip-sync animation
    *   `images`: Array of image objects with synchronized timing: [{url, description, step, start_time, duration}]

### 2. Dynamic Image Slideshow

*   When the backend returns image data in the `/ask` response, the frontend's `startImageSlideshow` function:
    *   Schedules each image to display at its LLM-calculated `start_time` using `setTimeout`.
    *   Example timing: Image 1 at 0s, Image 2 at 2.5s, Image 3 at 5.0s (synchronized with audio narration).
    *   Displays images in a top-right overlay (400px width) with description and step indicators.
    *   Logs timing information: "[2.5s] Showing image 2: 3 oranges (for 2.5s)".

### 3. Serving Audio Files

*   After receiving an `audio_url` (e.g., `/audio/some-uuid.wav`) from the `/ask` or `/speak` endpoints, the frontend constructs the full URL (e.g., `http://localhost:8000/audio/some-uuid.wav`).
*   It then makes a GET request to this URL to retrieve and play the audio file.

### 4. Serving Image Files

*   The backend serves generated images from the `/static/generated_images/` endpoint.
*   The frontend receives image URLs like `/static/generated_images/edu_xxxxx.png` and displays them at calculated times.

### 5. Text-to-Speech (TTS) for Summaries/Answers

*   When the frontend needs to convert text (e.g., a lecture summary) into speech, it sends a JSON POST request to the `/speak` endpoint with the text to be spoken.
*   The backend returns a JSON object with the audio URL and phoneme data, similar to the Q&A mode.

### 6. Lecture Mode (Proxied to Node.js)

*   For operations like listing, getting, or creating lectures, and generating quizzes, the frontend makes requests to the FastAPI backend's `/lectures` or `/quizzes/generate` endpoints.
*   FastAPI acts as a proxy, forwarding these requests to the Node.js API (`http://localhost:5000/api`) and returning the response to the frontend.

The `CORSMiddleware` configured in `app.py` ensures that the frontend can safely make these cross-origin requests to the backend during development.

---

## Image Generation Pipeline

The system uses a multi-stage AI pipeline for generating synchronized educational images:

### Stage 1: Content Analysis (Groq LLM)
*   Model: `llama-3.3-70b-versatile`
*   Input: RAG-generated teaching answer
*   Process:
    1.  Counts total words in the answer
    2.  Estimates speaking time at 2.5 words/second
    3.  Divides content into logical segments
    4.  Generates detailed image prompts for each segment
    5.  Calculates duration for each image based on content complexity
*   Output: JSON array of [{description, prompt, duration}]

### Stage 2: Image Generation (Hugging Face)
*   Model: `FLUX.1-schnell` (black-forest-labs)
*   Input: Image prompts from Stage 1
*   Process:
    1.  Generates educational images from text prompts
    2.  Saves images as PNG files with UUID filenames
    3.  Stores in `static/generated_images/` directory
*   Output: Image file paths

### Stage 3: Timing Synchronization
*   Calculates sequential timing based on LLM-provided durations:
    *   start_time = cumulative sum of previous durations
    *   end_time = start_time + current duration
*   Example: 3 images with durations [2.5s, 2.5s, 3.0s] → start times [0s, 2.5s, 5.0s]
*   Returns complete metadata: [{url, description, prompt, step, start_time, end_time, duration}]

### API Keys Required
*   `GROQ_API_KEY`: For LLM-based content analysis and timing calculation
*   `HUGGINGFACE_API_KEY`: For FLUX Schnell image generation (Note: Free tier has monthly credit limits)
*   `MURF_API_KEY`: For text-to-speech audio generation

### Current Limitations
*   Hugging Face free tier: Limited monthly credits (~100 images), 402 error when exceeded
*   Solution options: HF PRO subscription ($9/month for 20x credits), new account, or wait for monthly reset