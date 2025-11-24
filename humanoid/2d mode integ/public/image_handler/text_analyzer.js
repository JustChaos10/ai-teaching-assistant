/**
 * Text Analyzer - Parses AI teaching content to extract visual concepts
 * 
 * Identifies:
 * - Numbers and quantities
 * - Objects (apples, books, etc.)
 * - Math operations (addition, subtraction)
 * - Teaching scenarios
 */

class TextAnalyzer {
  constructor() {
    // Common objects for grade 1-2 teaching
    this.commonObjects = [
      'apple', 'apples', 'orange', 'oranges', 'banana', 'bananas',
      'book', 'books', 'pencil', 'pencils', 'ball', 'balls',
      'flower', 'flowers', 'star', 'stars', 'heart', 'hearts',
      'cat', 'cats', 'dog', 'dogs', 'bird', 'birds',
      'car', 'cars', 'tree', 'trees', 'house', 'houses'
    ];

    // Math operation patterns
    this.mathPatterns = {
      addition: /(\d+)\s*(?:and|plus|\+)\s*(\d+)/gi,
      subtraction: /(\d+)\s*(?:minus|-)\s*(\d+)/gi,
      equals: /(?:equals|is|=)\s*(\d+)/gi
    };
  }

  /**
   * Parse text to extract visual concepts for image generation
   * @param {string} text - AI output text
   * @returns {Array} Array of image prompts
   */
  parseText(text) {
    const visualConcepts = [];
    
    // Detect math operations with objects
    const mathScenarios = this.detectMathScenarios(text);
    if (mathScenarios.length > 0) {
      return mathScenarios;
    }

    // Detect counting scenarios
    const countingScenarios = this.detectCountingScenarios(text);
    if (countingScenarios.length > 0) {
      return countingScenarios;
    }

    // Fallback: extract general concepts
    const generalConcepts = this.detectGeneralConcepts(text);
    return generalConcepts;
  }

  /**
   * Detect math scenarios (e.g., "2 apples + 3 apples = 5 apples")
   */
  detectMathScenarios(text) {
    const scenarios = [];
    const textLower = text.toLowerCase();

    // Look for addition patterns
    const additionMatch = textLower.match(/(\d+)\s+(\w+)\s+(?:and|plus|\+)\s+(\d+)\s+(\w+)/i);
    
    if (additionMatch) {
      const [, num1, obj1, num2, obj2] = additionMatch;
      const object = this.normalizeObject(obj1);
      
      if (this.isCommonObject(object)) {
        // Generate 3 images: first group, second group, combined
        scenarios.push({
          type: 'math_addition',
          prompt: `${num1} ${object}, simple colorful illustration, educational style, white background`,
          description: `${num1} ${object}`,
          step: 1
        });
        
        scenarios.push({
          type: 'math_addition',
          prompt: `${num2} ${object}, simple colorful illustration, educational style, white background`,
          description: `${num2} ${object}`,
          step: 2
        });
        
        const total = parseInt(num1) + parseInt(num2);
        scenarios.push({
          type: 'math_addition',
          prompt: `${total} ${object}, simple colorful illustration, educational style, white background`,
          description: `${total} ${object} (total)`,
          step: 3
        });
      }
    }

    return scenarios;
  }

  /**
   * Detect simple counting scenarios
   */
  detectCountingScenarios(text) {
    const scenarios = [];
    const textLower = text.toLowerCase();

    // Pattern: "count the 5 apples" or "there are 3 books"
    const countPattern = /(?:count|there (?:are|is))\s+(\d+)\s+(\w+)/gi;
    let match;

    while ((match = countPattern.exec(textLower)) !== null) {
      const [, number, object] = match;
      const normalizedObject = this.normalizeObject(object);
      
      if (this.isCommonObject(normalizedObject)) {
        scenarios.push({
          type: 'counting',
          prompt: `${number} ${normalizedObject}, simple colorful illustration, educational style for children, white background`,
          description: `${number} ${normalizedObject}`,
          step: scenarios.length + 1
        });
      }
    }

    return scenarios;
  }

  /**
   * Detect general educational concepts
   */
  detectGeneralConcepts(text) {
    const concepts = [];
    const textLower = text.toLowerCase();

    // Extract any mentioned objects with numbers
    this.commonObjects.forEach(obj => {
      if (textLower.includes(obj)) {
        // Find if there's a number before this object
        const pattern = new RegExp(`(\\d+)\\s+${obj}`, 'gi');
        const match = textLower.match(pattern);
        
        if (match) {
          match.forEach((m, idx) => {
            const num = m.match(/\d+/)[0];
            concepts.push({
              type: 'general',
              prompt: `${num} ${obj}, simple colorful illustration, educational style, white background`,
              description: `${num} ${obj}`,
              step: idx + 1
            });
          });
        }
      }
    });

    return concepts;
  }

  /**
   * Normalize object names (singular/plural)
   */
  normalizeObject(obj) {
    obj = obj.toLowerCase().trim();
    // Remove plural 's' if present
    if (obj.endsWith('s') && obj.length > 1) {
      const singular = obj.slice(0, -1);
      if (this.commonObjects.includes(singular)) {
        return singular;
      }
    }
    return obj;
  }

  /**
   * Check if object is in common teaching objects
   */
  isCommonObject(obj) {
    return this.commonObjects.includes(obj) || this.commonObjects.includes(obj + 's');
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TextAnalyzer;
}
