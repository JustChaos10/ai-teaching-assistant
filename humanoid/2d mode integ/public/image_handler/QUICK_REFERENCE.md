# Image Handler - Quick Reference

## 🚀 Quick Start (3 Steps)

### 1. Add API Key
```json
// public/image_handler/config.json
{
  "apiProvider": "openai",
  "apiKeys": {
    "openai": "sk-your-actual-key-here"
  }
}
```

### 2. Load Scripts (in HTML)
```html
<script src="/image_handler/text_analyzer.js"></script>
<script src="/image_handler/image_generator.js"></script>
<script src="/image_handler/slideshow_manager.js"></script>
<script src="/image_handler/image_handler.js"></script>
```

### 3. Initialize & Use
```javascript
const handler = new ImageHandler('/image_handler/config.json');
await handler.init();

// Generate images from teaching content
await handler.processTeachingContent("2 apples + 3 apples = 5 apples", true);
```

## 📦 What's Included

| File | Purpose | Lines |
|------|---------|-------|
| `text_analyzer.js` | Parse text → extract concepts | 180 |
| `image_generator.js` | Concepts → generate images | 200 |
| `slideshow_manager.js` | Images → slideshow display | 400 |
| `image_handler.js` | Orchestrate everything | 150 |
| `example.html` | Standalone demo | 200 |
| **Total** | **Complete system** | **~930** |

## 🎯 Key Methods

```javascript
// ImageHandler
await handler.init()                          // Initialize (required first)
await handler.processTeachingContent(text)    // Full pipeline
handler.showSlideshow(images)                 // Manual slideshow
handler.stopSlideshow()                       // Stop slideshow
handler.clearCache()                          // Clear image cache

// TextAnalyzer
const concepts = analyzer.analyzeText(text)   // Parse text

// ImageGenerator
const url = await generator.generateImage(concept)        // Single image
const imgs = await generator.generateImageSequence(arr)   // Multiple images

// SlideshowManager
await manager.start(images)                   // Start slideshow
manager.stop()                                // Stop slideshow
```

## 💡 Example Scenarios

```javascript
// Math Addition
"2 apples + 3 apples = 5 apples"
→ 3 images: [2 apples] [3 apples] [5 apples]

// Counting
"Count from 1 to 5 stars"
→ 5 images: [1 star] [2 stars] ... [5 stars]

// Subtraction
"5 books - 2 books = 3 books"
→ 3 images: [5 books] [2 removed] [3 books]
```

## ⚙️ Configuration

```json
{
  "apiProvider": "openai",              // or "stabilityai"
  "imageSettings": {
    "quality": "standard",              // or "hd"
    "cacheEnabled": true                // save money!
  },
  "slideshowSettings": {
    "transitionDuration": 3000          // 3 sec per image
  }
}
```

## 🔧 Integration (React)

```javascript
// App.jsx
const imageHandlerRef = useRef(null);

useEffect(() => {
  async function init() {
    imageHandlerRef.current = new window.ImageHandler('/image_handler/config.json');
    await imageHandlerRef.current.init();
  }
  init();
}, []);

// When AI responds
const handleResponse = async (aiText) => {
  await imageHandlerRef.current.processTeachingContent(aiText, true);
};
```

## 💰 Costs (OpenAI DALL-E 3)

| Usage | Cost/Day |
|-------|----------|
| 10 questions with images | ~$0.40 |
| 50 questions | ~$2.00 |
| 100 questions | ~$4.00 |

**Tip:** Enable caching to reduce costs!

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Images not generating | Check API key in config.json |
| Slideshow not appearing | Verify `init()` was called |
| API errors | Check browser console for details |
| Rate limiting | Enable caching, reduce requests |

## 📚 Documentation Files

- **INTEGRATION_GUIDE.md** - Step-by-step React integration
- **IMPLEMENTATION_SUMMARY.md** - Complete technical overview
- **README.md** - Full API reference
- **example.html** - Working demo

## ✅ Testing Checklist

- [ ] Add OpenAI API key to config.json
- [ ] Open example.html in browser
- [ ] Test with: "2 apples + 3 apples = 5 apples"
- [ ] Verify slideshow appears with images
- [ ] Check browser console for logs
- [ ] Test integration with main app

## 🎉 Ready to Use!

```javascript
// Complete example
const handler = new ImageHandler('/image_handler/config.json');
await handler.init();

const result = await handler.processTeachingContent(
  "Look at 3 colorful balloons",
  true  // auto-play slideshow
);

console.log(result);
// {
//   success: true,
//   message: "Generated 1 images",
//   images: [...],
//   concepts: [...]
// }
```

---

**Need help?** Check INTEGRATION_GUIDE.md or IMPLEMENTATION_SUMMARY.md
