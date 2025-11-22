# Integration Guide: Image Handler with Main App

This guide shows how to integrate the image_handler module with your main teaching assistant application.

## Step 1: Add Scripts to index.html

Add the image handler scripts before your React app scripts:

```html
<!-- In public/index.html or your main HTML file -->
<head>
  <!-- Other head content -->
</head>
<body>
  <div id="root"></div>
  
  <!-- Image Handler Scripts (load before React app) -->
  <script src="/image_handler/text_analyzer.js"></script>
  <script src="/image_handler/image_generator.js"></script>
  <script src="/image_handler/slideshow_manager.js"></script>
  <script src="/image_handler/image_handler.js"></script>
  
  <!-- Your React app scripts -->
  <script type="module" src="/src/main.jsx"></script>
</body>
```

## Step 2: Update App.jsx

Add image handler initialization and integration:

```javascript
// src/App.jsx
import { useState, useEffect, useRef } from 'react';
import './App.css';
import Avatar from './components/Avatar';

function App() {
  const [mode, setMode] = useState('qa');
  const [message, setMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const imageHandlerRef = useRef(null);
  
  // Initialize image handler on mount
  useEffect(() => {
    async function initImageHandler() {
      try {
        imageHandlerRef.current = new window.ImageHandler(
          '/image_handler/config.json'
        );
        const initialized = await imageHandlerRef.current.init();
        
        if (initialized) {
          console.log('[App] Image Handler initialized successfully');
        } else {
          console.error('[App] Failed to initialize Image Handler');
        }
      } catch (error) {
        console.error('[App] Image Handler initialization error:', error);
      }
    }
    
    initImageHandler();
  }, []);
  
  const handleAskQuestion = async () => {
    if (!message.trim()) return;
    
    try {
      setIsListening(true);
      
      // Send question to backend
      const response = await fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: message }),
      });
      
      const data = await response.json();
      
      if (data.error) {
        console.error('Error:', data.error);
        return;
      }
      
      // Update chat history
      setChatHistory(prev => [...prev, {
        question: message,
        answer: data.answer,
        audioUrl: data.audio_url
      }]);
      
      // Generate images from AI response
      if (imageHandlerRef.current && data.answer) {
        console.log('[App] Processing teaching content for images...');
        
        const imageResult = await imageHandlerRef.current.processTeachingContent(
          data.answer,
          true  // Auto-start slideshow
        );
        
        if (imageResult.success && imageResult.images.length > 0) {
          console.log(`[App] Generated ${imageResult.images.length} educational images`);
        } else {
          console.log('[App] No visual concepts detected in this response');
        }
      }
      
      // Play audio response
      if (data.audio_url) {
        const audio = new Audio(data.audio_url);
        audio.play();
      }
      
      setMessage('');
    } catch (error) {
      console.error('Error asking question:', error);
    } finally {
      setIsListening(false);
    }
  };
  
  // Rest of your App component...
  return (
    <div className="App">
      {/* Your existing UI */}
    </div>
  );
}

export default App;
```

## Step 3: Configure API Keys

Edit `public/image_handler/config.json`:

```json
{
  "apiProvider": "openai",
  "apiKeys": {
    "openai": "sk-your-actual-openai-api-key-here"
  },
  "imageSettings": {
    "width": 512,
    "height": 512,
    "quality": "standard",
    "cacheEnabled": true
  },
  "slideshowSettings": {
    "transitionDuration": 3000,
    "autoPlay": true
  }
}
```

## Step 4: Optional - Manual Slideshow Control

Add buttons to manually control the slideshow:

```javascript
// In your component
const handleShowSlideshow = () => {
  if (imageHandlerRef.current && lastGeneratedImages) {
    imageHandlerRef.current.showSlideshow(lastGeneratedImages);
  }
};

const handleStopSlideshow = () => {
  if (imageHandlerRef.current) {
    imageHandlerRef.current.stopSlideshow();
  }
};

// In your JSX
<button onClick={handleShowSlideshow}>Show Images</button>
<button onClick={handleStopSlideshow}>Stop Slideshow</button>
```

## Step 5: Test Integration

1. Start your backend server:
```bash
cd backend
python teacher_chatbot_app.py
```

2. Start your frontend:
```bash
cd "humanoid/2d mode integ"
npm run dev
```

3. Test with example questions:
   - "What is 2 apples plus 3 apples?"
   - "Count from 1 to 5 stars"
   - "Show me 3 colorful balloons"

## Workflow

1. User asks question in Q&A mode
2. Backend generates AI response
3. Frontend receives response text
4. Image Handler analyzes text for visual concepts
5. If concepts found, generates images via API
6. Slideshow automatically displays images
7. Audio response plays simultaneously

## Advanced: Selective Image Generation

Only generate images for specific modes or keywords:

```javascript
const shouldGenerateImages = (text, mode) => {
  // Only generate for Q&A and Lecture modes
  if (mode !== 'qa' && mode !== 'lecture') return false;
  
  // Check if response contains numbers/objects
  const hasNumbers = /\d+/.test(text);
  const hasObjects = /(apple|star|book|ball|toy)/i.test(text);
  
  return hasNumbers || hasObjects;
};

// In handleAskQuestion:
if (imageHandlerRef.current && shouldGenerateImages(data.answer, mode)) {
  const result = await imageHandlerRef.current.processTeachingContent(
    data.answer,
    true
  );
}
```

## Troubleshooting

### Images not generating
- Check browser console for errors
- Verify API key is correct in config.json
- Test with example.html standalone demo
- Check CORS settings if using local files

### Slideshow not appearing
- Verify init() was called successfully
- Check that window.ImageHandler is defined
- Inspect slideshow-container element in DevTools

### Performance issues
- Enable caching: `"cacheEnabled": true`
- Reduce image dimensions in config
- Limit to 3-5 images per sequence

## API Costs

**OpenAI DALL-E 3:**
- Standard quality: $0.040 per image
- HD quality: $0.080 per image

**Estimated usage:**
- 10 questions with images/day = ~$0.40/day
- 100 questions/day = ~$4/day

**Tip:** Enable caching to reduce API calls for repeated concepts.
