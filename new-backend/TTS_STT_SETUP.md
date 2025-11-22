# TTS & STT Configuration Guide

## Overview

The AI Teaching Assistant supports both **English** and **Tamil** for:
- **STT (Speech-to-Text)**: Powered by Whisper
- **TTS (Text-to-Speech)**: Powered by Murf AI

## Current Status

| Component | English | Tamil | Status |
|-----------|---------|-------|--------|
| **STT (Speech-to-Text)** | ✅ Working | ✅ Working | Fully supported |
| **Language Detection** | ✅ Auto-detect | ✅ Auto-detect | Fully supported |
| **RAG System** | ✅ Uses context | ✅ **Bypassed** | Fixed (no hallucinations) |
| **LLM Response** | ✅ English text | ✅ Tamil text | Fully supported |
| **TTS (Text-to-Speech)** | ✅ English voice | ⚠️ **Needs config** | Requires setup |

## 🚨 CRITICAL: Tamil TTS Configuration

**Without proper configuration, Tamil audio will use English voice and sound garbled!**

### How to Fix:

1. **Get Tamil Voice ID from Murf AI:**
   - Go to: https://murf.ai/resources/voice-catalog
   - Filter by language: Tamil (தமிழ்)
   - Choose a voice (e.g., `ta-IN-kani`, `ta-IN-keerthi`)
   - Copy the voice ID

2. **Configure in `.env` file:**
   ```bash
   # In new-backend/.env
   MURF_VOICE_TA=ta-IN-kani  # Replace with your chosen Tamil voice ID
   ```

3. **Restart the backend:**
   ```bash
   # The system will now use proper Tamil voice
   ```

## How It Works

### 1. Speech-to-Text (STT)
- **Model**: Whisper "small" (faster_whisper)
- **Languages**: Auto-detects English or Tamil
- **Input**: Audio file (WAV)
- **Output**: Transcribed text + detected language

### 2. Language Detection & RAG
- **English Question** → Uses RAG to retrieve educational content
- **Tamil Question** → **Bypasses RAG** (prevents hallucinations from English documents)

### 3. LLM Response
- Generates age-appropriate response for 1st/2nd graders
- Responds in the **same language** as the question
- Tamil responses are generated directly by the LLM

### 4. Text-to-Speech (TTS)
- **Model**: Murf AI
- **English**: Uses `MURF_VOICE_EN` (default: `en-US-charles`)
- **Tamil**: Uses `MURF_VOICE_TA` (⚠️ must be configured!)

## Testing

### Test English:
```bash
# User speaks: "What is 2 + 2?"
# Expected: English voice responds with answer
```

### Test Tamil:
```bash
# User speaks: "இரண்டு கூட்டல் மூன்று?"
# Expected: Tamil voice responds with "ஐந்து" (Five)
# Without MURF_VOICE_TA: English voice tries to say Tamil words (garbled!)
```

## Warnings You Might See

### On Startup:
```
[WARNING] MURF_VOICE_TA not set in .env file!
[WARNING] Tamil TTS will use English voice - this will sound incorrect!
[TeacherChatbot] ⚠️ WARNING: Tamil voice not configured!
```

**Fix**: Set `MURF_VOICE_TA` in your `.env` file

### During Tamil TTS:
```
[TTS] ⚠️ WARNING: Generating Tamil audio with English voice!
[TTS] This will sound incorrect. Configure MURF_VOICE_TA in .env file.
```

**Fix**: Configure Tamil voice as described above

## API Endpoints

### `/ask` - Q&A Mode
```bash
POST /ask?language=auto
# Accepts: Audio file (WAV)
# Returns: {question, answer, audio_url, language, emotion, images}
# Supported languages: auto, en, ta
```

### Example:
```python
# Auto-detect language
response = requests.post(
    "http://localhost:8000/ask?language=auto",
    files={"file": open("question.wav", "rb")}
)
```

## Troubleshooting

### Tamil sounds weird/garbled:
**Problem**: Using English voice for Tamil text
**Solution**: Configure `MURF_VOICE_TA` in `.env` file

### Tamil questions get irrelevant answers:
**Problem**: RAG is retrieving English context
**Solution**: ✅ Already fixed! Tamil questions now bypass RAG

### Language not detected correctly:
**Problem**: Whisper auto-detection failure
**Solution**: Use explicit language parameter: `?language=ta` or `?language=en`

## Resources

- **Murf AI Voice Catalog**: https://murf.ai/resources/voice-catalog
- **Murf API Docs**: https://murf.ai/api
- **Whisper Languages**: https://github.com/openai/whisper#available-models-and-languages
- **GROQ API Keys**: https://console.groq.com/keys

## Quick Setup Checklist

- [ ] Set `GROQ_API_KEY` in `.env`
- [ ] Set `MURF_API_KEY` in `.env`
- [ ] Set `MURF_VOICE_EN` in `.env` (optional, has default)
- [ ] Set `MURF_VOICE_TA` in `.env` (⚠️ **CRITICAL for Tamil**)
- [ ] Restart backend
- [ ] Test English question
- [ ] Test Tamil question
- [ ] Verify Tamil audio uses Tamil voice

---

**Last Updated**: 2025-11-22
**Branch**: `claude/tamil-tts-fix-011wGAKbyqzUA5n5f7girxyG`
