# Image Generation System Setup Guide

## Overview
This system automatically generates educational images from AI teaching responses using:
1. **Groq LLM** - Analyzes teaching content and creates image prompts (FREE tier available)
2. **Google Imagen 3** - Generates images using Google's AI (FREE: 1,500 images/month)
3. **Backend** - Saves images and returns URLs to frontend
4. **Frontend** - Displays images in slideshow overlay

**No paid APIs required!** Both Groq and Google Imagen 3 have generous free tiers.

## Architecture Flow

```
User Question (Audio)
    ↓
Backend STT (Whisper)
    ↓
RAG System (GROQ LLM) → AI Answer
    ↓
Image Generator:
    ├─→ Groq LLM analyzes answer → image prompts
    ├─→ Banana API generates images
    └─→ Save images to static/generated_images/
    ↓
Return: {audio_url, images: [{url, description, step}]}
    ↓
Frontend:
    ├─→ Play audio (Avatar lip sync)
    └─→ Display images (slideshow overlay)
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd new-backend
pip install groq google-generativeai pillow
```

### 2. Get API Keys

#### Groq API Key (for LLM prompt generation)
✅ **Already configured** in your `.env` file!

#### Google API Key (for Imagen 3 - FREE image generation)
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)
5. **FREE TIER**: 1,500 images/month at no cost!

### 3. Configure Environment Variables

Add to your existing `.env` file in `new-backend/`:

```env
# API Keys (add this line)
GOOGLE_API_KEY=AIzaSy_your_google_api_key_here
```

Your complete `.env` should look like:

```env
# API Keys
MURF_API_KEY=your_murf_api_key_here
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
GOOGLE_API_KEY=AIzaSy_your_google_api_key_here  # Add this

# API Endpoints
LECTURE_API_BASE=http://localhost:5000/api

# Paths
OUTPUT_DIR=outputs

# Set tokenizers parallelism to avoid warnings
TOKENIZERS_PARALLELISM=false
```

### 4. Create Static Directory

```bash
cd new-backend
mkdir -p static/generated_images
```

### 5. Test the System

#### Backend Test
```bash
cd new-backend
python -c "
from image_generator import ImageGenerator
import os
groq_key = os.getenv('GROQ_API_KEY')
google_key = os.getenv('GOOGLE_API_KEY')
gen = ImageGenerator(groq_key, google_key)
prompts = gen.analyze_teaching_content('2 apples plus 3 apples equals 5 apples')
print(prompts)
"
```

#### Full Pipeline Test
```bash
# Start backend
cd new-backend
uvicorn app:app --reload --port 5000

# In frontend terminal
cd "humanoid/2d mode integ"
npm run dev

# Test: Record question "What is 2 apples plus 3 apples?"
```

## File Structure

```
new-backend/
├── image_generator.py        # NEW: Image generation logic
├── config.py                 # UPDATED: Added GROQ_API_KEY, BANANA_API_KEY
├── teacher_chatbot_app.py    # UPDATED: Integrated image generator
├── app.py                    # UPDATED: Serve static images, return images in response
├── static/
│   └── generated_images/     # NEW: Saved images directory
└── .env                      # NEW: Environment variables

humanoid/2d mode integ/src/
└── App.jsx                   # UPDATED: Display images in slideshow overlay
```

## How It Works

### 1. User Asks Question
```
User: "What is 2 apples plus 3 apples?"
```

### 2. RAG System Responds
```
AI Answer: "2 apples plus 3 apples equals 5 apples! Let me show you..."
```

### 3. Image Generator Analyzes Content
Groq LLM receives:
```
Prompt: "Analyze this teaching content and generate image prompts:
'2 apples plus 3 apples equals 5 apples!'"

Response:
[
  {"description": "Step 1", "prompt": "2 red apples, simple cartoon, white background"},
  {"description": "Step 2", "prompt": "3 red apples, simple cartoon, white background"},
  {"description": "Step 3", "prompt": "5 red apples, simple cartoon, white background"}
]
```

### 4. Google Imagen 3 Generates Images
For each prompt:
- Call Google Imagen 3 API with prompt
- Receive generated PIL image
- Save to `static/generated_images/edu_xxxxx.png`
- **FREE**: Uses Google's free tier (1,500 images/month)

### 5. Backend Returns Response
```json
{
  "audio_url": "/audio/response.wav",
  "images": [
    {"url": "/static/generated_images/edu_abc123.png", "description": "Step 1", "step": 1},
    {"url": "/static/generated_images/edu_def456.png", "description": "Step 2", "step": 2},
    {"url": "/static/generated_images/edu_ghi789.png", "description": "Step 3", "step": 3}
  ]
}
```

### 6. Frontend Displays
- Audio plays (Avatar lip syncs)
- Images appear in top-right overlay
- Auto-advance every 3 seconds
- Shows step indicators (dots)

## Customization

### Change Image Style
Edit `image_generator.py` line 45:
```python
"prompt": "2 red apples, photorealistic, studio lighting"  # Realistic
"prompt": "2 red apples, watercolor painting"              # Artistic
"prompt": "2 red apples, 3D render, Pixar style"          # 3D
```

### Change Slideshow Timing
Edit `App.jsx` line 90:
```javascript
}, 3000); // 3 seconds → change to 5000 for 5 seconds
```

### Change Image Position/Size
Edit `App.jsx` line 285-295:
```javascript
style={{
  top: '20px',      // Position from top
  right: '20px',    // Position from right
  width: '400px',   // Image container width
  // ...
}}
```

## Troubleshooting

### Images Not Generating
1. **Check API keys**: Verify GROQ_API_KEY and GOOGLE_API_KEY in .env file
2. **Check logs**: Backend console shows image generation progress
3. **Check directory**: Verify `static/generated_images/` exists
4. **Test Groq**: Run backend test script above
5. **Check Google quota**: Free tier is 1,500 images/month

### Images Not Displaying
1. **Check network**: Open browser DevTools → Network tab
2. **Check URLs**: Verify image URLs in response (should be `/static/generated_images/...`)
3. **Check CORS**: Backend should allow frontend origin
4. **Check console**: Frontend console shows image loading errors

### Google API Errors
1. **Check API key**: Verify GOOGLE_API_KEY in .env is correct
2. **Enable API**: Go to https://console.cloud.google.com/ and enable "Generative AI API"
3. **Check quota**: Free tier = 1,500 images/month
4. **Billing**: Some Google APIs require billing enabled (even for free tier)

### Slow Image Generation
- Each image takes 3-8 seconds
- 3 images = ~10-25 seconds total
- Consider:
  - Google Imagen 3 is generally fast
  - Reduce number of images per response
  - Pre-generate common scenarios

## API Costs & Limits

### ✅ FREE TIERS (No Credit Card Required)

**Groq (LLM for prompt generation):**
- FREE: Unlimited during beta
- Model: llama-3.3-70b-versatile
- Speed: Very fast responses

**Google Imagen 3 (Image generation):**
- FREE: 1,500 images per month
- Quality: High-quality AI images
- Speed: 3-8 seconds per image

### Estimated Monthly Usage
- 10 questions/day with images = ~300 images/month (FREE ✅)
- 50 questions/day = ~1,500 images/month (FREE ✅)
- 100 questions/day = ~3,000 images/month (Need paid plan ⚠️)

**Recommendation**: Start with free tier, monitor usage, upgrade only if needed.

## Alternative: If You Hit Free Tier Limits

If you exceed 1,500 images/month, you can:

## Alternative: If You Hit Free Tier Limits

If you exceed 1,500 images/month, you can:

1. **Enable Google Cloud Billing** (pay-as-you-go)
2. **Use OpenAI DALL-E** (~$0.02/image)
3. **Implement caching** to reuse common images
4. **Reduce images per response** (1-2 instead of 3-5)

## Next Steps

1. ✅ Get Google API key from https://aistudio.google.com/app/apikey
2. ✅ Add to .env file: `GOOGLE_API_KEY=AIzaSy...`
3. ✅ Install dependencies: `pip install google-generativeai pillow`
4. ✅ Test: Run backend test script
5. ✅ Test full pipeline with frontend
6. 🔄 Monitor usage in Google Cloud Console

## Support

For issues:
1. Check backend console logs
2. Check frontend browser console
3. Verify API keys are correct
4. Test each component individually
