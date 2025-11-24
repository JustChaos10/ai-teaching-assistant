# AI Teaching Assistant - 2D Avatar Frontend

An interactive educational platform featuring a 2D animated avatar with lip-sync, synchronized image slideshow, and voice interaction.

## Features

### 🎭 Animated Avatar
- **Live2D Cubism SDK** integration for realistic 2D character animation
- **Real-time lip-sync** synchronized with TTS audio using phoneme data
- **Emotion-based expressions** that match teaching content

### 🖼️ Dynamic Image Slideshow
- **LLM-calculated timing** - Groq analyzes content and assigns durations to each image
- **Synchronized display** - Images appear at precise times matching audio narration
- **Educational focus** - Images generated to support teaching concepts (numbers, objects, etc.)
- **Top-right overlay** with step indicators and descriptions

### 🎤 Voice Interaction
- **Speech-to-text** using Whisper model for question transcription
- **RAG-powered answers** with context from teaching documents
- **Multi-language support** (English, Tamil) with auto-detection
- **Natural TTS** using Murf.ai for high-quality voice responses

### 🎨 AI Image Generation
- **Pollinations.ai** for free, unlimited image generation
- **Groq LLM** analyzes teaching content and creates detailed prompts
- **Automatic timing** based on word count and speaking pace (2.5 words/sec)
- **No authentication required** - completely free service

## Tech Stack

- **React + Vite** - Fast development and build tooling
- **Live2D Cubism SDK** - 2D character animation
- **Web Audio API** - Audio playback and synchronization
- **FastAPI Backend** - Python-based API server
- **Groq LLM** - Content analysis and image prompt generation
- **Pollinations.ai** - Free AI image generation

## Setup

### Prerequisites
- Node.js (v18+)
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

```bash
cd "humanoid/2d mode integ"
npm install
npm run dev
```

Frontend will run on `http://localhost:5173`

### Backend Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

**Endpoints:**
- `POST /ask` - Send audio question, receive answer with audio + images
- `GET /audio/{filename}` - Retrieve TTS audio files
- `GET /static/generated_images/{filename}` - Retrieve generated educational images

**Response Format:**
```json
{
  "mode": "qa",
  "question": "What is 2 plus 3?",
  "answer": "2 plus 3 equals 5!",
  "language": "en",
  "audio_url": "/audio/response.wav",
  "emotion": "happy",
  "images": [
    {
      "url": "/static/generated_images/edu_abc123.png",
      "description": "2 objects",
      "step": 1,
      "start_time": 0.0,
      "duration": 2.5
    },
    {
      "url": "/static/generated_images/edu_def456.png",
      "description": "3 objects",
      "step": 2,
      "start_time": 2.5,
      "duration": 2.5
    },
    {
      "url": "/static/generated_images/edu_ghi789.png",
      "description": "5 total",
      "step": 3,
      "start_time": 5.0,
      "duration": 3.0
    }
  ]
}
```

## Image Slideshow System

### How It Works

1. **User asks question** via voice input
2. **Backend generates answer** using RAG system
3. **Groq LLM analyzes content:**
   - Counts words in answer
   - Estimates speaking time (2.5 words/second)
   - Divides content into logical segments
   - Generates image prompts with durations
4. **Pollinations.ai generates images** from prompts (free, unlimited)
5. **Backend calculates timing:**
   - Image 1: 0.0s - 2.5s
   - Image 2: 2.5s - 5.0s
   - Image 3: 5.0s - 8.0s
6. **Frontend displays images** at calculated times synchronized with audio

### Customization

**Image Display Position** (`src/App.jsx`):
```javascript
// Top-right overlay
top: '20px',
right: '20px',
width: '400px'
```

**Image Style** (Backend `image_generator.py`):
```python
# Change prompt template for different styles
"prompt": "2 apples, photorealistic"  # Realistic
"prompt": "2 apples, cartoon style"    # Cartoon
"prompt": "2 apples, watercolor"       # Artistic
```

## Development

### File Structure
```
src/
├── App.jsx              # Main component with image slideshow
├── main.jsx            # Entry point
└── assets/             # Static assets

public/
└── Live2D models/      # Avatar character files
```

### Key Features in Code

**Image Slideshow (`App.jsx`):**
```javascript
const startImageSlideshow = (imagesData) => {
  imagesData.forEach((img) => {
    const timer = setTimeout(() => {
      setCurrentImageIndex(images.findIndex(i => i.url === img.url));
      console.log(`[${img.start_time}s] Showing: ${img.description}`);
    }, img.start_time * 1000);
    imageTimersRef.current.push(timer);
  });
};
```

**Avatar Lip Sync:**
- Uses phoneme data from backend
- Synchronized with Web Audio API
- Live2D SDK controls mouth movements

## Troubleshooting

### Images Not Appearing
1. Check backend is running: `http://localhost:8000`
2. Verify images generated in `new-backend/static/generated_images/`
3. Check browser console for network errors
4. Ensure CORS is enabled in backend

### Audio/Lip-sync Issues
1. Verify microphone permissions
2. Check audio files in `new-backend/outputs/`
3. Ensure Web Audio API is supported in browser

### Timing Desynchronization
1. Check `start_time` values in backend response
2. Verify LLM duration calculations are reasonable
3. Adjust words/second rate in `image_generator.py`

## Credits

- **Live2D Integration** based on [r3f-lipsync-tutorial](https://github.com/wass08/r3f-lipsync-tutorial)
- **Pollinations.ai** for free image generation
- **Groq** for LLM-based content analysis
- **Murf.ai** for TTS voices
