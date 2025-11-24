/**
 * Image Generator - Generates images using AI APIs
 * 
 * Supports:
 * - Google Gemini (Imagen)
 * - OpenAI DALL-E
 * - Stability AI
 */

class ImageGenerator {
  constructor(config) {
    this.config = config;
    this.apiProvider = config.apiProvider || 'gemini';
    this.apiKey = config.apiKeys[this.apiProvider];
    this.cache = new Map();
  }

  /**
   * Generate an image from a text prompt
   * @param {Object} concept - Visual concept object from TextAnalyzer
   * @returns {Promise<string>} - Base64 image data or URL
   */
  async generateImage(concept) {
    // Check cache first
    const cacheKey = `${concept.prompt}_${concept.step}`;
    if (this.config.imageSettings.cacheEnabled && this.cache.has(cacheKey)) {
      console.log(`[Image Generator] Using cached image for: ${concept.description}`);
      return this.cache.get(cacheKey);
    }

    console.log(`[Image Generator] Generating image for: ${concept.description}`);
    console.log(`[Image Generator] Prompt: ${concept.prompt}`);

    try {
      let imageData;
      
      switch (this.apiProvider) {
        case 'gemini':
          imageData = await this.generateWithGemini(concept.prompt);
          break;
        case 'openai':
          imageData = await this.generateWithOpenAI(concept.prompt);
          break;
        case 'stabilityai':
          imageData = await this.generateWithStabilityAI(concept.prompt);
          break;
        default:
          throw new Error(`Unsupported API provider: ${this.apiProvider}`);
      }

      // Cache the result
      if (this.config.imageSettings.cacheEnabled) {
        this.cache.set(cacheKey, imageData);
      }

      return imageData;
    } catch (error) {
      console.error(`[Image Generator] Error generating image:`, error);
      throw error;
    }
  }

  /**
   * Generate image using Google Gemini API
   */
  async generateWithGemini(prompt) {
    const API_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent';
    
    // Note: As of now, Gemini doesn't have a public image generation API
    // This is a placeholder for when Google releases Imagen API publicly
    // For now, you might want to use DALL-E or Stability AI
    
    console.warn('[Image Generator] Gemini image generation not yet publicly available. Use OpenAI or Stability AI instead.');
    
    // Placeholder implementation
    const response = await fetch(`${API_ENDPOINT}?key=${this.apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: `Generate an image: ${prompt}`
          }]
        }]
      })
    });

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    // Process and return image data
    return data;
  }

  /**
   * Generate image using OpenAI DALL-E
   */
  async generateWithOpenAI(prompt) {
    const API_ENDPOINT = 'https://api.openai.com/v1/images/generations';
    
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: 'dall-e-3',
        prompt: prompt,
        n: 1,
        size: '1024x1024',
        quality: this.config.imageSettings.quality || 'standard',
        style: 'natural'
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`OpenAI API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    return data.data[0].url; // Returns image URL
  }

  /**
   * Generate image using Stability AI
   */
  async generateWithStabilityAI(prompt) {
    const API_ENDPOINT = 'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image';
    
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        text_prompts: [
          {
            text: prompt,
            weight: 1
          }
        ],
        cfg_scale: 7,
        height: this.config.imageSettings.height || 512,
        width: this.config.imageSettings.width || 512,
        samples: 1,
        steps: 30
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Stability AI error: ${error.message || response.statusText}`);
    }

    const data = await response.json();
    // Convert base64 to data URL
    return `data:image/png;base64,${data.artifacts[0].base64}`;
  }

  /**
   * Generate multiple images in sequence
   * @param {Array} concepts - Array of visual concepts
   * @returns {Promise<Array>} - Array of generated images
   */
  async generateImageSequence(concepts) {
    const images = [];
    
    for (const concept of concepts) {
      try {
        const imageData = await this.generateImage(concept);
        images.push({
          ...concept,
          imageUrl: imageData,
          generatedAt: new Date().toISOString()
        });
        
        // Add small delay between requests to avoid rate limiting
        await this.delay(500);
      } catch (error) {
        console.error(`[Image Generator] Failed to generate image for step ${concept.step}:`, error);
        // Add placeholder for failed image
        images.push({
          ...concept,
          imageUrl: null,
          error: error.message
        });
      }
    }
    
    return images;
  }

  /**
   * Utility: delay function
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Clear image cache
   */
  clearCache() {
    this.cache.clear();
    console.log('[Image Generator] Cache cleared');
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ImageGenerator;
}
