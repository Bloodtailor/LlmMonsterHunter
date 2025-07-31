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
    .getPropertyValue(`--color-${colorName}`)
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
 * Color structure for organizing colors by families
 * This maps to what's defined in theme.css
 */
export const COLOR_FAMILIES = {
  red: ['intense', 'warm', 'deep', 'crimson', 'cherry'],
  orange: ['vibrant', 'warm', 'golden', 'flame', 'amber'],
  yellow: ['bright', 'golden', 'electric', 'warm', 'citrus'],
  green: ['nature', 'electric', 'forest', 'mint', 'emerald'],
  blue: ['electric', 'cool', 'deep', 'ice', 'ocean', 'sky'],
  purple: ['mystic', 'deep', 'soft', 'electric', 'cosmic'],
  pink: ['vibrant', 'soft', 'electric', 'rose'],
  white: ['pure', 'soft', 'pearl', 'silver'],
  gray: ['light', 'medium', 'dark', 'smoke'],
  black: ['pure', 'soft', 'void'],
  rainbow: ['1', '2', '3', '4', '5', '6'],
  gold: ['bright', 'rich'],
  silver: ['bright', 'chrome'],
  copper: ['bright', 'warm']
};

/**
 * Generate all available color options for dropdowns
 * Reads actual hex values from CSS at runtime
 * @returns {Array} Array of color objects with name, displayName, hex, etc.
 */
export const getAllColors = () => {
  const colors = [];
  
  Object.entries(COLOR_FAMILIES).forEach(([hue, variants]) => {
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
  
  Object.entries(COLOR_FAMILIES).forEach(([hue, variants]) => {
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
  const variants = COLOR_FAMILIES[hue] || [];
  
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
};

// Utility function to capitalize strings
const capitalize = (str) => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Export common hue names for easy access
export const HUE_NAMES = Object.keys(COLOR_FAMILIES);

export default {
  getColor,
  getColorVar,
  getAllColors,
  getColorsByFamily,
  getColorsInFamily,
  colorExists,
  getRandomColor,
  setColor,
  HUE_NAMES,
  COLOR_FAMILIES
};