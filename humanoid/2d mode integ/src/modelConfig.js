/**
 * Live2D Model Configuration
 * 
 * Change the modelName to switch between different characters.
 * Available models: 'Haru', 'Hiyori', 'Mao', 'Mark', 'Natori', 'Rice', 'Wanko'
 */

export const modelConfig = {
  // Current model to display
  modelName: 'Hiyori',
  
  // Base path for all models (relative to public folder)
  basePath: '/Resources',
  
  // Model-specific settings (optional overrides)
  models: {
    Haru: {
      scale: 0.8,
      position: { x: 0.0, y: 0.0 }
    },
    Hiyori: {
      scale: 1.2,
      position: { x: 0.0, y: 0.0 }
    },
    Mao: {
      scale: 0.8,
      position: { x: 0.0, y: 0.0 }
    },
    Mark: {
      scale: 0.8,
      position: { x: 0.0, y: 0.0 }
    },
    Natori: {
      scale: 0.8,
      position: { x: 0.0, y: 0.0 }
    },
    Rice: {
      scale: 0.8,
      position: { x: 0.0, y: 0.0 }
    },
    Wanko: {
      scale: 0.8,
      position: { x: 0.0, y: 0.0 }
    }
  }
};

/**
 * Get the full model path
 */
export function getModelPath(modelName = modelConfig.modelName) {
  return `${modelConfig.basePath}/${modelName}/${modelName}.model3.json`;
}

/**
 * Get model settings
 */
export function getModelSettings(modelName = modelConfig.modelName) {
  return modelConfig.models[modelName] || modelConfig.models.Haru;
}
