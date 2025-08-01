// CoCaTok Component - Interactive 3D spinning Collectable Card Tokens
// Always spinning, bouncing cards that stop and face you on hover
// Click to spin fast, face forward, explode dramatically, and disappear forever
// Perfect for rare collectibles found in dungeons

import React, { useState } from 'react';
import HueBasedExplosion from '../primitives/Explosion/HueBasedExplosion';
import { getColor, getColorVar } from '../../styles/color';
import './CoCaTok.css';

/**
 * Interactive collectable card token that spins in 3D space
 * @param {object} props - CoCaTok props
 * @param {string} props.color - Color name from color system (e.g., 'red-intense', 'blue-electric')
 * @param {string} props.size - Size variant ('sm', 'md', 'lg', 'xl')
 * @param {string} props.emoji - Emoji to display on the card (required)
 * @param {Function} props.onActivate - Callback when card completes its animation
 * @param {boolean} props.disabled - Disable interaction
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} CoCaTok component
 */
function CoCaTok({
  color = 'purple-mystic',
  size = 'md',
  emoji = '✨',
  onActivate = () => {},
  disabled = false,
  className = '',
  style = {},
  ...rest
}) {
  const [isSpinning, setIsSpinning] = useState(false);
  const [isExploding, setIsExploding] = useState(false);

  // Extract hue from color name (e.g., 'red-intense' → 'red')
  const extractHue = (colorName) => {
    if (!colorName || typeof colorName !== 'string') {
      return 'purple'; // default fallback
    }
    
    // Split on first dash and take the first part
    const parts = colorName.split('-');
    return parts[0] || 'purple';
  };

  const cardHue = extractHue(color);

  // Handle card click - trigger the full animation sequence
  const handleClick = async () => {
    if (disabled || isSpinning) return;

    setIsSpinning(true);

    // Wait for spin animation to complete (3 seconds)
    setTimeout(() => {
      setIsExploding(true);
      
      // Wait for explode animation (1.5 seconds), then trigger callback but DON'T reset
      setTimeout(() => {
        onActivate(color, emoji); // Pass color and emoji to callback
        // Card stays exploded/gone forever - no reset!
      }, 1500);
    }, 3000);
  };

  // Build CSS classes
  const cardClasses = [
    'cocatok',
    `cocatok-${size}`,
    isSpinning && 'cocatok-spinning',
    isExploding && 'cocatok-exploding',
    disabled && 'cocatok-disabled',
    className
  ].filter(Boolean).join(' ');

  // Get the color values for styling
  const primaryColor = getColor(color);
  const colorVar = getColorVar(color);
  
  // Create dynamic styles based on color
  const dynamicStyle = {
    '--card-primary-color': primaryColor,
    '--card-border-color': primaryColor,
    '--card-shadow-color': primaryColor ? `${primaryColor}30` : 'rgba(0,0,0,0.3)', // 30% opacity
    ...style
  };

  // Apply color-based styling to the card faces
  const cardFaceStyle = {
    background: `linear-gradient(135deg, ${primaryColor}dd 0%, ${primaryColor}aa 100%)`,
    borderColor: primaryColor,
    color: primaryColor,
    boxShadow: `0 4px 8px ${primaryColor ? `${primaryColor}30` : 'rgba(0,0,0,0.3)'}`
  };

  return (
    <div
      className={cardClasses}
      style={dynamicStyle}
      onClick={handleClick}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label={`${color} collectible card token with ${emoji} - explodes with ${cardHue} themed effects`}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      {...rest}
    >
      <div className="cocatok-inner">
        {/* Front side - card layout like loading spinner + bouncing emoji in image */}
        <div className="cocatok-front" style={cardFaceStyle}>
          <div className="card-image-area">
            <div className="front-emoji">{emoji}</div>
          </div>
          <div className="card-title-line"></div>
          <div className="card-text-line"></div>
          <div className="card-text-line short"></div>
        </div>
        
        {/* Back side - emoji display */}
        <div className="cocatok-back" style={cardFaceStyle}>
          <div className="cocatok-emoji">{emoji}</div>
        </div>
      </div>
      
      {/* EPIC Explosion effect using HueBasedExplosion component! */}
      {isExploding && (
        <HueBasedExplosion 
          hue={cardHue}
          size="lg"
          intensity={1.2}
          speed={1.1}
        />
      )}
    </div>
  );
}

// Size constants
export const COCATOK_SIZES = {
  SM: 'sm',
  MD: 'md', 
  LG: 'lg',
  XL: 'xl'
};

export default CoCaTok;