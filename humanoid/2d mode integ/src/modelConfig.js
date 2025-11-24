/**
 * Live2D Model Configuration
 * 
 * Change the modelName to switch between different characters.
 * Available models: 'Haru', 'Hiyori', 'Mao', 'Mark', 'Natori', 'Rice', 'Wanko', 'chitose'
 */

export const modelConfig = {
  // Current model to display
  modelName: 'chitose',
  
  // Base path for all models (relative to public folder)
  basePath: '/Resources',
  
  // Model-specific settings (optional overrides)
  models: {
    Haru: {
      scale: 1.2,
      position: { x: 0.0, y: -0.1 }
    },
    Hiyori: {
      scale: 1.2,
      position: { x: 0.0, y: 0.0 }
    },
    Mao: {
      scale: 1.2,
      position: { x: 0.0, y: 0.0 }
    },
    Mark: {
      scale: 1.2,
      position: { x: 0.0, y: 0.0 }
    },
    Natori: {
      scale: 1.2,
      position: { x: 0.0, y: 0.0 }
    },
    Rice: {
      scale: 1.2,
      position: { x: 0.0, y: 0.0 }
    },
    Wanko: {
      scale: 1.2,
      position: { x: 0.0, y: 0.0 }
    },
    chitose: {
      scale: 1.6,
      position: { x: 0.0, y: -0.5 }
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
