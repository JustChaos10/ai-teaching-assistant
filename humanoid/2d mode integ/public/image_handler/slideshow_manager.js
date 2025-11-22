/**
 * Slideshow Manager - Displays generated images as a slideshow
 * 
 * Features:
 * - Sequential image display with transitions
 * - Auto-play with configurable timing
 * - Manual navigation (next/previous)
 * - Overlay mode (displays over main content)
 */

class SlideshowManager {
  constructor(config) {
    this.config = config;
    this.images = [];
    this.currentIndex = 0;
    this.isPlaying = false;
    this.intervalId = null;
    this.container = null;
  }

  /**
   * Initialize the slideshow UI
   */
  init() {
    // Create slideshow container
    this.container = document.createElement('div');
    this.container.id = 'slideshow-container';
    this.container.className = 'slideshow-hidden';
    
    this.container.innerHTML = `
      <div class="slideshow-overlay">
        <div class="slideshow-content">
          <button class="slideshow-close" aria-label="Close slideshow">&times;</button>
          
          <div class="slideshow-image-wrapper">
            <img id="slideshow-image" src="" alt="Educational visual" />
            <div class="slideshow-description"></div>
          </div>
          
          <div class="slideshow-controls">
            <button class="slideshow-btn" id="prev-btn" aria-label="Previous">&#8249;</button>
            <div class="slideshow-indicators"></div>
            <button class="slideshow-btn" id="next-btn" aria-label="Next">&#8250;</button>
          </div>
          
          <div class="slideshow-progress-bar">
            <div class="slideshow-progress-fill"></div>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(this.container);
    this.attachEventListeners();
    this.injectStyles();
  }

  /**
   * Inject CSS styles
   */
  injectStyles() {
    const styleId = 'slideshow-styles';
    if (document.getElementById(styleId)) return;
    
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .slideshow-hidden {
        display: none;
      }
      
      .slideshow-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.9);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease-in;
      }
      
      .slideshow-content {
        position: relative;
        max-width: 90%;
        max-height: 90%;
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
      }
      
      .slideshow-close {
        position: absolute;
        top: 10px;
        right: 10px;
        background: transparent;
        border: none;
        font-size: 36px;
        color: #666;
        cursor: pointer;
        z-index: 10001;
        line-height: 1;
        padding: 5px 10px;
      }
      
      .slideshow-close:hover {
        color: #000;
      }
      
      .slideshow-image-wrapper {
        text-align: center;
        margin-bottom: 20px;
      }
      
      #slideshow-image {
        max-width: 100%;
        max-height: 60vh;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.5s ease-out;
      }
      
      .slideshow-description {
        margin-top: 15px;
        font-size: 18px;
        color: #333;
        font-weight: 500;
      }
      
      .slideshow-controls {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        margin-top: 20px;
      }
      
      .slideshow-btn {
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 32px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.3s;
      }
      
      .slideshow-btn:hover {
        background: #45a049;
      }
      
      .slideshow-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
      }
      
      .slideshow-indicators {
        display: flex;
        gap: 8px;
      }
      
      .slideshow-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #ddd;
        cursor: pointer;
        transition: background 0.3s;
      }
      
      .slideshow-indicator.active {
        background: #4CAF50;
      }
      
      .slideshow-progress-bar {
        width: 100%;
        height: 4px;
        background: #eee;
        border-radius: 2px;
        margin-top: 15px;
        overflow: hidden;
      }
      
      .slideshow-progress-fill {
        height: 100%;
        background: #4CAF50;
        width: 0%;
        transition: width 0.1s linear;
      }
      
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      
      @keyframes slideIn {
        from { transform: translateX(20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `;
    
    document.head.appendChild(style);
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    // Close button
    this.container.querySelector('.slideshow-close').addEventListener('click', () => {
      this.stop();
    });
    
    // Navigation buttons
    this.container.querySelector('#prev-btn').addEventListener('click', () => {
      this.previous();
    });
    
    this.container.querySelector('#next-btn').addEventListener('click', () => {
      this.goToNext();
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (!this.isPlaying) return;
      
      if (e.key === 'ArrowLeft') this.previous();
      if (e.key === 'ArrowRight') this.goToNext();
      if (e.key === 'Escape') this.stop();
    });
  }

  /**
   * Load and start slideshow
   * @param {Array} images - Array of image objects with imageUrl and description
   */
  async start(images) {
    if (!images || images.length === 0) {
      console.error('[Slideshow] No images provided');
      return;
    }
    
    this.images = images.filter(img => img.imageUrl); // Filter out failed images
    if (this.images.length === 0) {
      console.error('[Slideshow] All images failed to generate');
      return;
    }
    
    this.currentIndex = 0;
    this.isPlaying = true;
    this.container.classList.remove('slideshow-hidden');
    
    this.renderIndicators();
    this.showImage(0);
    this.startAutoPlay();
    
    console.log(`[Slideshow] Started with ${this.images.length} images`);
  }

  /**
   * Render indicator dots
   */
  renderIndicators() {
    const indicatorsContainer = this.container.querySelector('.slideshow-indicators');
    indicatorsContainer.innerHTML = '';
    
    this.images.forEach((_, index) => {
      const indicator = document.createElement('div');
      indicator.className = 'slideshow-indicator';
      if (index === 0) indicator.classList.add('active');
      
      indicator.addEventListener('click', () => {
        this.showImage(index);
      });
      
      indicatorsContainer.appendChild(indicator);
    });
  }

  /**
   * Display image at specified index
   */
  showImage(index) {
    if (index < 0 || index >= this.images.length) return;
    
    this.currentIndex = index;
    const image = this.images[index];
    
    // Update image and description
    const imgElement = this.container.querySelector('#slideshow-image');
    const descElement = this.container.querySelector('.slideshow-description');
    
    imgElement.src = image.imageUrl;
    descElement.textContent = image.description;
    
    // Update indicators
    const indicators = this.container.querySelectorAll('.slideshow-indicator');
    indicators.forEach((ind, i) => {
      ind.classList.toggle('active', i === index);
    });
    
    // Update navigation buttons
    this.container.querySelector('#prev-btn').disabled = (index === 0);
    this.container.querySelector('#next-btn').disabled = (index === this.images.length - 1);
    
    // Reset progress bar
    this.resetProgressBar();
  }

  /**
   * Go to next image
   */
  goToNext() {
    if (this.currentIndex < this.images.length - 1) {
      this.showImage(this.currentIndex + 1);
    } else {
      // Loop back to first image
      this.showImage(0);
    }
  }

  /**
   * Go to previous image
   */
  previous() {
    if (this.currentIndex > 0) {
      this.showImage(this.currentIndex - 1);
    }
  }

  /**
   * Start auto-play
   */
  startAutoPlay() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    
    const duration = this.config.slideshowSettings?.transitionDuration || 3000;
    
    // Animate progress bar
    this.animateProgressBar(duration);
    
    this.intervalId = setInterval(() => {
      if (this.currentIndex < this.images.length - 1) {
        this.goToNext();
      } else {
        // End slideshow after last image
        this.stop();
      }
    }, duration);
  }

  /**
   * Animate progress bar
   */
  animateProgressBar(duration) {
    const progressFill = this.container.querySelector('.slideshow-progress-fill');
    progressFill.style.width = '0%';
    
    // Force reflow
    progressFill.offsetHeight;
    
    progressFill.style.transition = `width ${duration}ms linear`;
    progressFill.style.width = '100%';
  }

  /**
   * Reset progress bar
   */
  resetProgressBar() {
    const progressFill = this.container.querySelector('.slideshow-progress-fill');
    progressFill.style.transition = 'none';
    progressFill.style.width = '0%';
    
    // Restart animation
    const duration = this.config.slideshowSettings?.transitionDuration || 3000;
    setTimeout(() => {
      this.animateProgressBar(duration);
    }, 50);
  }

  /**
   * Stop slideshow
   */
  stop() {
    this.isPlaying = false;
    this.container.classList.add('slideshow-hidden');
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    
    console.log('[Slideshow] Stopped');
  }

  /**
   * Check if slideshow is currently playing
   */
  getIsPlaying() {
    return this.isPlaying;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SlideshowManager;
}
