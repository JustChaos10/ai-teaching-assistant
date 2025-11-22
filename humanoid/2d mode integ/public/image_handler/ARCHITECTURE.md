# Image Handler System Architecture

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Q&A Mode: "What is 2 apples plus 3 apples?"                    │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (RAG SYSTEM)                          │
│  • Whisper STT (voice → text)                                   │
│  • GROQ LLM (question → answer)                                 │
│  • Murf TTS (answer → audio)                                    │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI Response: "2 apples plus 3 apples equals 5 apples!"         │
└─────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
        ┌───────────────────┐       ┌──────────────────┐
        │  AUDIO PLAYBACK   │       │  IMAGE HANDLER   │
        │  (existing flow)  │       │  (NEW MODULE)    │
        └───────────────────┘       └──────────────────┘
                                             │
                                             ▼
                    ┌────────────────────────────────────────┐
                    │     TEXT ANALYZER (text_analyzer.js)   │
                    │                                         │
                    │  Input: "2 apples + 3 apples = 5"      │
                    │                                         │
                    │  Detects:                               │
                    │  ├─ Math pattern (+ operation)         │
                    │  ├─ Objects (apples)                   │
                    │  └─ Numbers (2, 3, 5)                  │
                    │                                         │
                    │  Output: [                              │
                    │    {prompt: "2 apples", step: 1},      │
                    │    {prompt: "3 apples", step: 2},      │
                    │    {prompt: "5 apples", step: 3}       │
                    │  ]                                      │
                    └────────────────────────────────────────┘
                                             │
                                             ▼
                    ┌────────────────────────────────────────┐
                    │  IMAGE GENERATOR (image_generator.js)  │
                    │                                         │
                    │  For each concept:                      │
                    │                                         │
                    │  ┌──────────────────────────────┐      │
                    │  │ Check Cache                  │      │
                    │  │  ↓ if not cached             │      │
                    │  │ API Call (OpenAI/Stability)  │      │
                    │  │  ↓                            │      │
                    │  │ Generate Image               │      │
                    │  │  ↓                            │      │
                    │  │ Cache Result                 │      │
                    │  └──────────────────────────────┘      │
                    │                                         │
                    │  Output: [                              │
                    │    {imageUrl: "data:...", step: 1},    │
                    │    {imageUrl: "data:...", step: 2},    │
                    │    {imageUrl: "data:...", step: 3}     │
                    │  ]                                      │
                    └────────────────────────────────────────┘
                                             │
                                             ▼
                    ┌────────────────────────────────────────┐
                    │ SLIDESHOW MANAGER (slideshow_mgr.js)   │
                    │                                         │
                    │  ┌──────────────────────────────┐      │
                    │  │ Create Overlay UI            │      │
                    │  │  ↓                            │      │
                    │  │ Display Image 1 (3 sec)      │      │
                    │  │  ↓                            │      │
                    │  │ Transition → Image 2 (3 sec) │      │
                    │  │  ↓                            │      │
                    │  │ Transition → Image 3 (3 sec) │      │
                    │  │  ↓                            │      │
                    │  │ End Slideshow / Loop         │      │
                    │  └──────────────────────────────┘      │
                    │                                         │
                    │  Features:                              │
                    │  • Progress bar                         │
                    │  • Navigation dots                      │
                    │  • Prev/Next buttons                    │
                    │  • Keyboard controls                    │
                    │  • Auto-play timer                      │
                    └────────────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER SEES RESULT                              │
│                                                                  │
│  🔊 Audio: AI explains "2 apples plus 3 apples equals 5"        │
│  🖼️ Visual: Slideshow shows:                                    │
│     Step 1: Image of 2 apples                                   │
│     Step 2: Image of 3 apples                                   │
│     Step 3: Image of 5 apples                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction

```
ImageHandler (orchestrator)
    │
    ├─→ TextAnalyzer
    │   └─→ analyzeText() → concepts[]
    │
    ├─→ ImageGenerator
    │   ├─→ Check cache
    │   ├─→ Call API (DALL-E/Stability)
    │   └─→ generateImageSequence() → images[]
    │
    └─→ SlideshowManager
        ├─→ Create UI overlay
        ├─→ start(images)
        └─→ Auto-play with transitions
```

## Data Flow

```
┌──────────────────┐
│ AI Response Text │
└────────┬─────────┘
         │
         ▼
┌────────────────────┐      ┌──────────────────────┐
│ Visual Concepts    │      │ {                    │
│ Array              │ ───→ │   type: "math",      │
│                    │      │   prompt: "2 apples",│
└────────────────────┘      │   description: "...",│
         │                  │   step: 1            │
         │                  │ }                    │
         ▼                  └──────────────────────┘
┌────────────────────┐
│ Generated Images   │      ┌──────────────────────┐
│ Array              │ ───→ │ {                    │
│                    │      │   imageUrl: "...",   │
└────────────────────┘      │   description: "...",│
         │                  │   step: 1            │
         │                  │ }                    │
         ▼                  └──────────────────────┘
┌────────────────────┐
│ Slideshow Display  │
│ (User Interface)   │
└────────────────────┘
```

## Module Dependencies

```
image_handler.js (main)
    │
    ├── requires: text_analyzer.js
    ├── requires: image_generator.js
    ├── requires: slideshow_manager.js
    └── requires: config.json

text_analyzer.js
    └── requires: config.json

image_generator.js
    ├── requires: config.json
    └── external: OpenAI API / Stability AI API

slideshow_manager.js
    └── requires: config.json
```

## File Structure

```
public/image_handler/
│
├── config.json              # Configuration (API keys, settings)
│
├── text_analyzer.js         # Step 1: Parse text
│   └── Methods:
│       ├── analyzeText()
│       ├── detectMathScenarios()
│       ├── detectCountingScenarios()
│       └── detectGeneralConcepts()
│
├── image_generator.js       # Step 2: Generate images
│   └── Methods:
│       ├── generateImage()
│       ├── generateImageSequence()
│       ├── generateWithOpenAI()
│       ├── generateWithStabilityAI()
│       └── clearCache()
│
├── slideshow_manager.js     # Step 3: Display slideshow
│   └── Methods:
│       ├── init()
│       ├── start()
│       ├── stop()
│       ├── showImage()
│       ├── goToNext()
│       └── previous()
│
├── image_handler.js         # Orchestrator
│   └── Methods:
│       ├── init()
│       ├── processTeachingContent()
│       ├── showSlideshow()
│       ├── stopSlideshow()
│       └── clearCache()
│
└── Documentation:
    ├── QUICK_REFERENCE.md
    ├── INTEGRATION_GUIDE.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── ARCHITECTURE.md (this file)
    └── example.html
```

## State Management

### ImageHandler State
```javascript
{
  config: {...},              // Loaded configuration
  textAnalyzer: TextAnalyzer, // Instance
  imageGenerator: ImageGenerator, // Instance
  slideshowManager: SlideshowManager // Instance
}
```

### ImageGenerator State
```javascript
{
  config: {...},
  apiProvider: "openai",
  apiKey: "sk-...",
  cache: Map<string, imageData> // Cached images
}
```

### SlideshowManager State
```javascript
{
  images: [...],           // Current image set
  currentIndex: 0,         // Current slide
  isPlaying: false,        // Playing status
  intervalId: number,      // Timer ID
  container: HTMLElement   // UI element
}
```

## Execution Timeline

```
Time   Action
─────  ──────────────────────────────────────────────────
0ms    User asks question
10ms   Backend processes with RAG
1500ms Backend returns AI response + audio
1501ms Frontend receives response
1502ms Audio starts playing
1503ms ImageHandler.processTeachingContent() called
1504ms TextAnalyzer extracts 3 concepts
1505ms ImageGenerator starts generating image 1
3500ms Image 1 generated (cached)
3501ms 500ms delay
4001ms ImageGenerator starts generating image 2
6500ms Image 2 generated (cached)
6501ms 500ms delay
7001ms ImageGenerator starts generating image 3
9500ms Image 3 generated (cached)
9501ms All images ready
9502ms SlideshowManager.start() called
9503ms Slideshow overlay appears
9504ms Image 1 displayed (3 seconds)
12504ms Transition to image 2 (3 seconds)
15504ms Transition to image 3 (3 seconds)
18504ms Slideshow ends
```

## Error Handling Flow

```
processTeachingContent()
    │
    ├─→ TextAnalyzer fails
    │   └─→ Return {success: false, message: "No concepts"}
    │
    ├─→ ImageGenerator fails for image
    │   └─→ Add {imageUrl: null, error: "message"}
    │   └─→ Continue with next image
    │
    └─→ SlideshowManager fails
        └─→ Log error, slideshow doesn't appear
        └─→ Return {success: false, message: "error"}
```

## Caching Strategy

```
Generate Request → Check Cache
                        │
            ┌───────────┴───────────┐
            │                       │
        Found in                Not Found
        Cache                       │
            │                       │
            ↓                       ↓
    Return Cached          API Call (DALL-E)
    Image (instant)                 │
                                    ↓
                            Generate Image
                                    │
                                    ↓
                            Save to Cache
                                    │
                                    ↓
                            Return Image
```

## Integration Points

### With React App
```javascript
App.jsx
  ├── Initialize ImageHandler (useEffect)
  ├── Store in useRef
  └── Call processTeachingContent() on AI response

Avatar.jsx
  ├── (No changes needed)
  └── Continues handling Live2D and lip sync

Backend
  ├── (No changes needed)
  └── Returns text response as usual
```

### With Backend (Future)
```
Option 1: Frontend Generation (current)
  Frontend receives text → generates images → displays

Option 2: Backend Generation (future)
  Backend receives question → generates images → returns URLs
  Frontend receives URLs → displays slideshow
```

## Performance Considerations

### Optimization Strategies
1. **Caching**: Reuse generated images for repeated concepts
2. **Delays**: 500ms between API calls to avoid rate limits
3. **Parallel**: Generate images sequentially (not parallel) to manage rate limits
4. **Quality**: Use "standard" quality (faster, cheaper) vs "hd"
5. **Dimensions**: 512x512 generates faster than 1024x1024

### Resource Usage
- **Memory**: ~5MB per cached image (base64)
- **Network**: ~100KB per generated image
- **API Time**: ~2-3 seconds per image
- **Total Time**: ~10 seconds for 3-image sequence

## Security Considerations

1. **API Keys**: Stored in config.json (should be in .env for production)
2. **CORS**: No issues when served from same origin
3. **Rate Limiting**: Built-in delays prevent API abuse
4. **Input Validation**: TextAnalyzer filters malicious input
5. **XSS Prevention**: All content properly escaped in UI

---

**Module Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Production Ready ✅
