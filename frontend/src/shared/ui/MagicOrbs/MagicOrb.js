// TreasureCard Component - Interactive 3D spinning magical treasure cards
// Always spinning, bouncing cards that stop and face you on hover
// Click to spin fast, face forward, explode dramatically, and disappear forever
// Perfect for rare collectibles found in dungeons

import React, { useState } from 'react';
import { Explosion } from '../Explosion';
import './MagicOrb.css';

/**
 * Interactive magical treasure card that spins in 3D space
 * @param {object} props - TreasureCard props
 * @param {string} props.type - Card type ('health', 'fire', 'ice', 'lightning', 'magic', 'poison')
 * @param {string} props.size - Size variant ('sm', 'md', 'lg', 'xl')
 * @param {string} props.emoji - Emoji to display on the back (defaults based on type)
 * @param {Function} props.onActivate - Callback when card completes its animation
 * @param {boolean} props.disabled - Disable interaction
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} TreasureCard component
 */
function TreasureCard({
  type = 'magic',
  size = 'md',
  emoji = null,
  onActivate = () => {},
  disabled = false,
  className = '',
  style = {},
  ...rest
}) {
  const [isSpinning, setIsSpinning] = useState(false);
  const [isExploding, setIsExploding] = useState(false);

  // Default emojis for each type
  const defaultEmojis = {
    health: '❤️',
    fire: '🔥',
    ice: '❄️',
    lightning: '⚡',
    magic: '✨',
    poison: '☠️',
    shield: '🛡️',
    strength: '💪',
    speed: '💨'
  };

  const orbEmoji = emoji || defaultEmojis[type] || '✨';

  // Handle orb click - trigger the full animation sequence
  const handleClick = async () => {
    if (disabled || isSpinning) return;

    setIsSpinning(true);

    // Wait for spin animation to complete (3 seconds)
    setTimeout(() => {
      setIsExploding(true);
      
      // Wait for explode animation (1.5 seconds), then trigger callback but DON'T reset
      setTimeout(() => {
        onActivate(type); // Trigger the callback
        // Card stays exploded/gone forever - no reset!
      }, 1500);
    }, 3000);
  };

  // Build CSS classes
  const orbClasses = [
    'magic-orb',
    `magic-orb-${type}`,
    `magic-orb-${size}`,
    isSpinning && 'magic-orb-spinning',
    isExploding && 'magic-orb-exploding',
    disabled && 'magic-orb-disabled',
    className
  ].filter(Boolean).join(' ');

  return (
    <div
      className={orbClasses}
      style={style}
      onClick={handleClick}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label={`${type} treasure card`}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      {...rest}
    >
      <div className="magic-orb-inner">
        {/* Front side - card layout like loading spinner + bouncing emoji in image */}
        <div className="magic-orb-front">
          <div className="card-image-area">
            <div className="front-emoji">{orbEmoji}</div>
          </div>
          <div className="card-title-line"></div>
          <div className="card-text-line"></div>
          <div className="card-text-line short"></div>
        </div>
        
        {/* Back side - emoji instead of diagonal pattern */}
        <div className="magic-orb-back">
          <div className="orb-emoji">{orbEmoji}</div>
        </div>
      </div>
      
      {/* EPIC Explosion effect using new Explosion component! */}
      {isExploding && (
        <Explosion />
      )}
    </div>
  );
}

// Size constants
export const TREASURE_SIZES = {
  SM: 'sm',
  MD: 'md', 
  LG: 'lg',
  XL: 'xl'
};

// Type constants  
export const TREASURE_TYPES = {
  HEALTH: 'health',
  FIRE: 'fire',
  ICE: 'ice', 
  LIGHTNING: 'lightning',
  MAGIC: 'magic',
  POISON: 'poison',
  SHIELD: 'shield',
  STRENGTH: 'strength',
  SPEED: 'speed'
};

export default TreasureCard;