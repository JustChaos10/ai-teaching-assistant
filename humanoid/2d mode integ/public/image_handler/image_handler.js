/**
 * Image Handler - Main orchestrator for educational image generation
 * 
 * Integrates:
 * - TextAnalyzer: Parses AI teaching content
 * - ImageGenerator: Generates images via API
 * - SlideshowManager: Displays images sequentially
 */

class ImageHandler {
  constructor(configPath = './config.json') {
    this.config = null;
    this.textAnalyzer = null;
    this.imageGenerator = null;
    this.slideshowManager = null;
    this.configPath = configPath;
  }

  /**
   * Initialize the image handler
   */
  async init() {
    try {
      // Load configuration
      const response = await fetch(this.configPath);
      this.config = await response.json();
      
      // Initialize components
      this.textAnalyzer = new TextAnalyzer(this.config);
      this.imageGenerator = new ImageGenerator(this.config);
      this.slideshowManager = new SlideshowManager(this.config);
      this.slideshowManager.init();
      
      console.log('[Image Handler] Initialized successfully');
      return true;
    } catch (error) {
      console.error('[Image Handler] Initialization failed:', error);
      return false;
    }
  }

  /**
   * Process AI teaching content and generate images
   * @param {string} text - AI response text (e.g., "2 apples + 3 apples = 5 apples")
   * @param {boolean} autoPlay - Whether to auto-start slideshow
   * @returns {Promise<Object>} - Result object with images and status
   */
  async processTeachingContent(text, autoPlay = true) {
    console.log('[Image Handler] Processing teaching content:', text);
    
    try {
      // Step 1: Analyze text to extract visual concepts
      const visualConcepts = this.textAnalyzer.analyzeText(text);
      
      if (!visualConcepts || visualConcepts.length === 0) {
        console.log('[Image Handler] No visual concepts detected in text');
        return {
          success: false,
          message: 'No visual concepts found',
          images: []
        };
      }
      
      console.log(`[Image Handler] Detected ${visualConcepts.length} visual concepts:`, visualConcepts);
      
      // Step 2: Generate images for each concept
      const generatedImages = await this.imageGenerator.generateImageSequence(visualConcepts);
      
      const successfulImages = generatedImages.filter(img => img.imageUrl);
      const failedImages = generatedImages.filter(img => !img.imageUrl);
      
      console.log(`[Image Handler] Generated ${successfulImages.length}/${generatedImages.length} images successfully`);
      
      if (failedImages.length > 0) {
        console.warn('[Image Handler] Failed images:', failedImages);
      }
      
      // Step 3: Display slideshow if auto-play enabled
      if (autoPlay && successfulImages.length > 0) {
        await this.slideshowManager.start(successfulImages);
      }
      
      return {
        success: true,
        message: `Generated ${successfulImages.length} images`,
        images: generatedImages,
        concepts: visualConcepts
      };
      
    } catch (error) {
      console.error('[Image Handler] Error processing teaching content:', error);
      return {
        success: false,
        message: error.message,
        images: []
      };
    }
  }

  /**
   * Manually trigger slideshow with existing images
   * @param {Array} images - Array of image objects
   */
  showSlideshow(images) {
    if (!this.slideshowManager) {
      console.error('[Image Handler] Slideshow manager not initialized');
      return;
    }
    
    this.slideshowManager.start(images);
  }

  /**
   * Stop current slideshow
   */
  stopSlideshow() {
    if (this.slideshowManager) {
      this.slideshowManager.stop();
    }
  }

  /**
   * Check if slideshow is currently playing
   */
  isSlideshowPlaying() {
    return this.slideshowManager ? this.slideshowManager.getIsPlaying() : false;
  }

  /**
   * Clear image cache
   */
  clearCache() {
    if (this.imageGenerator) {
      this.imageGenerator.clearCache();
    }
  }

  /**
   * Update configuration
   * @param {Object} newConfig - New configuration object
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    // Update component configs
    if (this.textAnalyzer) this.textAnalyzer.config = this.config;
    if (this.imageGenerator) {
      this.imageGenerator.config = this.config;
      this.imageGenerator.apiProvider = this.config.apiProvider;
      this.imageGenerator.apiKey = this.config.apiKeys[this.config.apiProvider];
    }
    if (this.slideshowManager) this.slideshowManager.config = this.config;
    
    console.log('[Image Handler] Configuration updated');
  }

  /**
   * Get current configuration
   */
  getConfig() {
    return this.config;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ImageHandler;
}

// Make available globally for browser usage
if (typeof window !== 'undefined') {
  window.ImageHandler = ImageHandler;
  window.TextAnalyzer = TextAnalyzer;
  window.ImageGenerator = ImageGenerator;
  window.SlideshowManager = SlideshowManager;
}
