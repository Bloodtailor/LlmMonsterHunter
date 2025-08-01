// HueBasedExplosion.js - Explosion component that uses all color variants from a hue family
// Takes a hue like 'red', 'blue', 'purple' and creates explosion with all variants of that hue

import React from 'react';
import ExplosionEngine from './ExplosionEngine.js';
import { getColorsInFamily, getRandomColor } from '../../styles/color.js';
import './explosion.css';

/**
 * Explosion component that uses all color variants from a specific hue family
 * @param {string} props.hue - Color hue family name (e.g., 'red', 'blue', 'purple')
 * @param {string} props.size - Size: 'sm', 'md', 'lg', 'xl', 'massive' (default: 'md')
 * @param {number} props.intensity - Intensity multiplier (0.5-3, default: 1)
 * @param {number} props.speed - Speed multiplier (0.5-3, default: 1) 
 * @param {boolean} props.autoStart - Start immediately (default: true)
 * @param {Function} props.onComplete - Callback when finished
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} ExplosionPreset with hue-based colors
 */
function HueBasedExplosion({
  hue = 'red',
  size = 'md',
  intensity = 1,
  speed = 1,
  autoStart = true,
  onComplete = () => {},
  className = '',
  style = {},
  ...rest
}) {

  // Get all color variants for the specified hue
  const getHueColors = () => {
    const familyColors = getColorsInFamily(hue);
    
    if (familyColors.length === 0) {
      console.warn(`No colors found for hue: ${hue}. Using random color.`);
      const randomColor = getRandomColor();
      return randomColor ? [randomColor.hex] : ['#ff6348']; // fallback
    }
    
    // Extract hex values from the color objects
    return familyColors.map(color => color.hex);
  };

  const hueColors = getHueColors();

  return (
    <ExplosionEngine
      colors={hueColors}
      size={size}
      intensity={intensity}
      speed={speed}
      autoStart={autoStart}
      onComplete={onComplete}
      className={className}
      style={style}
      {...rest}
    />
  );
}

export default HueBasedExplosion;