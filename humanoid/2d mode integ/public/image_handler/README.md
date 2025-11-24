# Image Handler for AI Teaching Assistant

This module handles dynamic image generation based on AI teaching content.

## Features

- **Text Analysis**: Parses AI output to identify visual concepts
- **Image Generation**: Uses AI image generation API (e.g., Gemini, DALL-E)
- **Slideshow Display**: Shows generated images in sequence
- **Educational Context**: Specifically designed for teaching scenarios (counting, objects, math)

## Structure

```
image_handler/
├── README.md                  # This file
├── config.json               # Configuration for API keys and settings
├── image_generator.js        # Core image generation logic
├── text_analyzer.js          # Parses AI text to extract visual concepts
├── slideshow_manager.js      # Manages image slideshow display
└── generated_images/         # Cache for generated images
```

## Example Usage

For teaching "2 apples + 3 apples = 5 apples":
1. Text analyzer identifies: "2 apples", "3 apples", "5 apples"
2. Image generator creates 3 images
3. Slideshow displays them in sequence

## API Support

- Gemini (Google AI)
- DALL-E (OpenAI)
- Stable Diffusion
- Other text-to-image APIs
