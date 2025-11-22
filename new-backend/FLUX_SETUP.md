# FLUX Schnell Image Generation Setup

## What is FLUX Schnell?

FLUX Schnell is a state-of-the-art, FREE image generation model by Black Forest Labs that:
- Generates high-quality images in 1-4 steps (very fast!)
- Completely open-source (Apache 2.0 license)
- Can be used for personal, scientific, and commercial purposes
- 12 billion parameter transformer model

## 🎉 FREE Option (Already Configured!)

**You don't need any API key!** The system is already configured to use Hugging Face's FREE Inference API:

✅ **No signup required**
✅ **No credit card needed**
✅ **Unlimited usage** (with rate limits)
✅ **Already working** - just ensure `GROQ_API_KEY` is set in your `.env` file

### Current Setup Status:
- ✅ GROQ_API_KEY: Required (you already have this)
- ⚠️ REPLICATE_API_KEY: Optional (for faster, more reliable generation)

## 🚀 Optional: Replicate API (Faster & More Reliable)

If you want faster image generation with higher reliability, you can optionally use Replicate:

### How to Get Replicate API Key (Optional):

1. **Sign up for Replicate**
   - Go to https://replicate.com/
   - Click "Sign Up" (free account)
   - Verify your email

2. **Get Your API Token**
   - Go to https://replicate.com/account/api-tokens
   - Click "Create token"
   - Copy your API token (starts with `r8_...`)

3. **Add to .env File**
   ```env
   REPLICATE_API_KEY=r8_your_token_here
   ```

4. **Pricing**
   - Free tier: $5 credit (enough for ~500 images)
   - FLUX Schnell: ~$0.003 per image (very cheap!)
   - After free credit: Pay-as-you-go

## Usage Examples

### Using FREE Hugging Face (Current Default):
```python
# Just ensure GROQ_API_KEY is set - that's it!
# System automatically uses Hugging Face Inference API
```

### Using Replicate (Optional):
```python
# Add REPLICATE_API_KEY to .env
# System automatically detects and uses Replicate for faster generation
```

## Comparison

| Feature | Hugging Face (FREE) | Replicate (Paid) |
|---------|---------------------|------------------|
| **Cost** | FREE | ~$0.003/image |
| **Speed** | 10-30 seconds | 2-5 seconds |
| **Reliability** | May timeout | Very reliable |
| **Setup** | None needed ✅ | API key required |
| **Rate Limits** | Yes | Higher limits |

## Testing Your Setup

1. Ensure `.env` has `GROQ_API_KEY`
2. Start your backend: `python app.py`
3. Ask a question through the frontend
4. Check terminal for:
   ```
   [Image Generator] Initialized with FLUX Schnell
   [Image Generator] Using: Hugging Face Inference (FREE)
   [Image Generator] Calling FLUX Schnell with prompt: ...
   [Image Generator] ✅ Image saved: ...
   ```

## Troubleshooting

### "Model loading, waiting 20 seconds"
- **Normal behavior** - Hugging Face loads models on-demand
- First request takes longer, subsequent requests are faster
- If this happens often, consider using Replicate API

### No images generated
- Check `GROQ_API_KEY` is set in `.env`
- Check terminal for error messages
- Verify `static/generated_images/` directory exists

### Want even faster generation?
- Add `REPLICATE_API_KEY` to `.env`
- System automatically switches to Replicate

## Model Information

- **Name**: FLUX.1 [schnell]
- **Developer**: Black Forest Labs
- **Parameters**: 12 billion
- **License**: Apache 2.0 (commercial use allowed)
- **Speed**: 1-4 inference steps
- **Quality**: State-of-the-art (competitive with DALL-E, Midjourney)

## Links

- Replicate: https://replicate.com/black-forest-labs/flux-schnell
- Hugging Face: https://huggingface.co/black-forest-labs/FLUX.1-schnell
- Official Repo: https://github.com/black-forest-labs/flux
