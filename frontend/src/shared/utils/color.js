// Color Utilities - Reads colors from CSS custom properties
// Colors are defined in theme.css and accessed via JavaScript
// Perfect for dropdowns, color pickers, and dynamic styling

/**
 * Get a color value from CSS custom properties
 * @param {string} colorName - Color name like 'red-intense' 
 * @returns {string} Hex color value
 */
export const getColor = (colorName) => {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(`--base-color-${colorName}`)
    .trim();
};

/**
 * Get CSS custom property string for a color
 * @param {string} colorName - Color name like 'red-intense'
 * @returns {string} CSS var() string
 */
export const getColorVar = (colorName) => {
  return `var(--color-${colorName})`;
};

/**
 * Dynamically generate COLOR_FAMILIES from CSS custom properties
 * Reads all --color-* properties and builds the family structure
 * @returns {Object} Color families object organized by hue
 */
const generateColorFamilies = () => {
  const families = {};
  
  try {
    // Get all stylesheets from the document
    const styleSheets = Array.from(document.styleSheets);
    
    styleSheets.forEach(styleSheet => {
      try {
        // Get CSS rules from each stylesheet
        const rules = Array.from(styleSheet.cssRules || styleSheet.rules || []);
        
        rules.forEach(rule => {
          // Look for :root rules (where CSS custom properties are defined)
          if (rule.selectorText === ':root' && rule.style) {
            // Iterate through all style properties
            for (let i = 0; i < rule.style.length; i++) {
              const propertyName = rule.style[i];
              
              // Check if it's a color custom property
              if (propertyName.startsWith('--base-color-')) {
                // Extract the color name (remove --color- prefix)
                const colorName = propertyName.replace('--base-color-', '');
                
                // Split into hue and variant
                const parts = colorName.split('-');
                if (parts.length >= 2) {
                  const hue = parts[0];
                  const variant = parts.slice(1).join('-'); // Handle multi-part variants like 'bright-electric'
                  
                  // Initialize hue array if needed
                  if (!families[hue]) {
                    families[hue] = [];
                  }
                  
                  // Add variant if not already present
                  if (!families[hue].includes(variant)) {
                    families[hue].push(variant);
                  }
                }
              }
            }
          }
        });
      } catch (e) {
        // Skip stylesheets that can't be accessed (CORS issues, etc.)
        console.warn('Could not access stylesheet:', e);
      }
    });
  } catch (e) {
    console.error('Error generating color families:', e);
  }
  
  return families;
};

/**
 * Alternative approach using getComputedStyle
 * Less reliable but simpler - use as fallback
 * @returns {Object} Color families object
 */
const generateColorFamiliesFromComputed = () => {
  const families = {};
  const computedStyles = getComputedStyle(document.documentElement);
  
  // This approach tries to iterate through computed styles
  // Note: This may not capture all custom properties reliably
  for (const propertyName in computedStyles) {
    if (typeof propertyName === 'string' && propertyName.startsWith('--base-color-')) {
      const colorName = propertyName.replace('--base-color-', '');
      const parts = colorName.split('-');
      
      if (parts.length >= 2) {
        const hue = parts[0];
        const variant = parts.slice(1).join('-');
        
        if (!families[hue]) {
          families[hue] = [];
        }
        
        if (!families[hue].includes(variant)) {
          families[hue].push(variant);
        }
      }
    }
  }
  
  return families;
};

/**
 * Robust color families generator with fallback
 * Tries multiple approaches to ensure reliability
 * @returns {Object} Color families object
 */
const getColorFamiliesFromCSS = () => {
  // Try the stylesheet approach first (most reliable)
  let families = generateColorFamilies();
  
  // If no families found, try the computed style approach
  if (Object.keys(families).length === 0) {
    families = generateColorFamiliesFromComputed();
  }
  
  // If still no families, return empty object (don't fall back to hardcoded)
  if (Object.keys(families).length === 0) {
    console.warn('No color families could be generated from CSS');
  }
  
  return families;
};

// Lazy-loaded color families - only generated when first accessed
let _colorFamilies = null;

/**
 * Get color families dynamically from CSS
 * Cached after first call for performance
 * @returns {Object} Color families object organized by hue
 */
export const getColorFamilies = () => {
  if (!_colorFamilies) {
    _colorFamilies = getColorFamiliesFromCSS();
  }
  return _colorFamilies;
};

/**
 * Force refresh of color families cache
 * Useful if CSS has been modified dynamically
 */
export const refreshColorFamilies = () => {
  _colorFamilies = null;
  return getColorFamilies();
};

/**
 * Generate all available color options for dropdowns
 * Reads actual hex values from CSS at runtime
 * @returns {Array} Array of color objects with name, displayName, hex, etc.
 */
export const getAllColors = () => {
  const colors = [];
  const colorFamilies = getColorFamilies();
  
  Object.entries(colorFamilies).forEach(([hue, variants]) => {
    variants.forEach(variant => {
      const colorName = `${hue}-${variant}`;
      const displayName = `${capitalize(hue)} ${capitalize(variant)}`;
      const hex = getColor(colorName);
      
      // Only add if CSS variable exists and has a value
      if (hex) {
        colors.push({
          name: colorName,           // 'red-intense'
          displayName: displayName,  // 'Red Intense'  
          hex: hex,                  // '#ff2d2d'
          hue: hue,                  // 'red'
          variant: variant,          // 'intense'
          cssVar: getColorVar(colorName) // 'var(--color-red-intense)'
        });
      }
    });
  });
  
  return colors;
};

/**
 * Get colors organized by hue family for grouped dropdowns
 * @returns {Array} Array of hue groups with their color options
 */
export const getColorsByFamily = () => {
  const families = [];
  const colorFamilies = getColorFamilies();
  
  Object.entries(colorFamilies).forEach(([hue, variants]) => {
    const colors = variants.map(variant => {
      const colorName = `${hue}-${variant}`;
      const hex = getColor(colorName);
      
      return hex ? {
        name: colorName,
        displayName: capitalize(variant),
        hex: hex,
        cssVar: getColorVar(colorName)
      } : null;
    }).filter(Boolean); // Remove null values
    
    if (colors.length > 0) {
      families.push({
        label: capitalize(hue),
        hue: hue,
        colors: colors
      });
    }
  });
  
  return families;
};

/**
 * Get all colors of a specific hue
 * @param {string} hue - Color hue like 'red', 'blue', etc.
 * @returns {Array} Array of color variants for that hue
 */
export const getColorsInFamily = (hue) => {
  const colorFamilies = getColorFamilies();
  const variants = colorFamilies[hue] || [];
  
  return variants.map(variant => {
    const colorName = `${hue}-${variant}`;
    const hex = getColor(colorName);
    
    return hex ? {
      name: colorName,
      displayName: capitalize(variant),
      hex: hex,
      cssVar: getColorVar(colorName)
    } : null;
  }).filter(Boolean);
};

/**
 * Check if a color exists in CSS
 * @param {string} colorName - Color name like 'red-intense'
 * @returns {boolean} True if color exists
 */
export const colorExists = (colorName) => {
  const hex = getColor(colorName);
  return hex && hex !== '';
};

/**
 * Get random color from available colors
 * @param {string} [hue] - Optional hue to limit selection to
 * @returns {Object} Random color object
 */
export const getRandomColor = (hue = null) => {
  const colors = hue ? getColorsInFamily(hue) : getAllColors();
  const randomIndex = Math.floor(Math.random() * colors.length);
  return colors[randomIndex];
};

/**
 * Set CSS custom property value dynamically
 * @param {string} colorName - Color name like 'red-intense'
 * @param {string} hexValue - New hex color value
 */
export const setColor = (colorName, hexValue) => {
  document.documentElement.style.setProperty(`--color-${colorName}`, hexValue);
  // Refresh color families cache since CSS has changed
  refreshColorFamilies();
};

/**
 * Get all available hue names from CSS
 * @returns {Array} Array of hue names
 */
export const getHueNames = () => {
  const colorFamilies = getColorFamilies();
  return Object.keys(colorFamilies);
};

// Utility function to capitalize strings
const capitalize = (str) => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Export hue names for backward compatibility
export const HUE_NAMES = getHueNames();

// Backward compatibility - expose COLOR_FAMILIES as getter
export const COLOR_FAMILIES = getColorFamilies();

export default {
  getColor,
  getColorVar,
  getAllColors,
  getColorsByFamily,
  getColorsInFamily,
  colorExists,
  getRandomColor,
  setColor,
  getColorFamilies,
  refreshColorFamilies,
  getHueNames,
  get HUE_NAMES() { return getHueNames(); },
  get COLOR_FAMILIES() { return getColorFamilies(); }
};