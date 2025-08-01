// ExplosionPreset.js - High-level preset-based explosion interface
// Uses ExplosionEngine internally with predefined configurations
// Perfect for game events and common use cases

import React from 'react';
import ExplosionEngine from './ExplosionEngine.js';
import { EXPLOSION_TYPES, EXPLOSION_CONFIGS } from './ExplosionConstants.js';
import { COLOR_THEMES } from '../../constants/constants.js';
import { getColor, getColorsInFamily, getRandomColor } from '../../styles/color.js';

/**
 * High-level preset-based explosion component
 * @param {string} props.type - Explosion type from EXPLOSION_TYPES (required)
 * @param {string} props.colorTheme - Color theme from COLOR_THEMES or color family name (default: 'fire')
 * @param {string} props.size - Size: 'sm', 'md', 'lg', 'xl', 'massive' (default: 'md')
 * @param {number} props.intensity - Intensity multiplier (0.5-3, default: 1)
 * @param {number} props.speed - Speed multiplier (0.5-3, default: 1)
 * @param {boolean} props.randomize - Randomize type and colors (default: false)
 * @param {Function} props.onComplete - Callback when finished
 * @param {boolean} props.autoStart - Start immediately (default: true)
 */
function ExplosionPreset({
  type = 'particle-storm',
  colorTheme = 'fire',
  size = 'md',
  intensity = 1,
  speed = 1,
  randomize = false,
  onComplete = () => {},
  autoStart = true,
  className = '',
  style = {},
  ...rest
}) {

  // Generate random configuration
  const generateRandomConfig = () => {
    const types = Object.values(EXPLOSION_TYPES);
    const themes = Object.keys(COLOR_THEMES);
    const sizes = ['sm', 'md', 'lg', 'xl', 'massive'];
    
    return {
      type: types[Math.floor(Math.random() * types.length)],
      colorTheme: themes[Math.floor(Math.random() * themes.length)],
      size: sizes[Math.floor(Math.random() * sizes.length)],
      intensity: 0.8 + Math.random() * 1.5,
      speed: 0.7 + Math.random() * 1.8
    };
  };

  // Get final configuration (randomized or props)
  const config = randomize ? generateRandomConfig() : { type, colorTheme, size, intensity, speed };

  // Get explosion preset configuration
  const explosionConfig = EXPLOSION_CONFIGS[config.type];
  if (!explosionConfig) {
    console.warn(`Unknown explosion type: ${config.type}. Using particle-storm.`);
    explosionConfig = EXPLOSION_CONFIGS['particle-storm'];
  }

  // Convert color theme to actual colors
  const getThemeColors = () => {
    // Check if it's a predefined color theme
    if (COLOR_THEMES[config.colorTheme]) {
      return COLOR_THEMES[config.colorTheme].map(colorName => getColor(colorName) || '#ff6348');
    } 
    
    // Check if it's a color family (red, blue, etc.)
    const familyColors = getColorsInFamily(config.colorTheme);
    if (familyColors.length > 0) {
      return familyColors.slice(0, 4).map(color => color.hex);
    }
    
    // Single color
    const singleColor = getColor(config.colorTheme);
    if (singleColor) {
      return [singleColor];
    }
    
    // Fallback to fire theme
    return COLOR_THEMES.fire.map(colorName => getColor(colorName) || '#ff6348');
  };

  const themeColors = getThemeColors();

  // Map preset configuration to ExplosionEngine props
  const engineProps = {
    particles: explosionConfig.particles,
    streaks: explosionConfig.streaks,
    rings: explosionConfig.rings,
    fragments: explosionConfig.fragments,
    waves: explosionConfig.waves,
    sparks: explosionConfig.sparks,
    pattern: explosionConfig.pattern,
    hasFlash: explosionConfig.hasFlash,
    hasShockwave: explosionConfig.hasShockwave,
    colors: themeColors,
    size: config.size,
    intensity: config.intensity,
    speed: config.speed,
    onComplete,
    autoStart,
    className,
    style,
    ...rest
  };

  return <ExplosionEngine {...engineProps} />;
}

export default ExplosionPreset;