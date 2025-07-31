// Explosion Component - Epic particle explosion system
// Configurable, reusable explosions for any game event
// Perfect for treasure cards, spell effects, monster defeats, etc.

import React, { useEffect, useState } from 'react';
import './Explosion.css';

/**
 * Epic explosion component with configurable particle effects
 * @param {object} props - Explosion props
 * @param {string} props.type - Explosion type ('burst', 'sparkle', 'fire', 'ice', 'lightning', 'magic')
 * @param {string} props.size - Size variant ('sm', 'md', 'lg', 'xl', 'massive')
 * @param {string} props.color - Color theme ('primary', 'fire', 'ice', 'lightning', 'magic', 'treasure')
 * @param {number} props.duration - Animation duration in milliseconds (default: 1500)
 * @param {number} props.particleCount - Number of particles (default: based on size)
 * @param {Function} props.onComplete - Callback when explosion finishes
 * @param {boolean} props.autoStart - Start explosion immediately (default: true)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} Explosion component
 */
function Explosion({
  type = 'burst',
  size = 'md',
  color = 'primary',
  duration = 1500,
  particleCount = null, // Auto-calculate based on size if not provided
  onComplete = () => {},
  autoStart = true,
  className = '',
  style = {},
  ...rest
}) {
  const [isExploding, setIsExploding] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  // Auto-calculate particle count based on size
  const getParticleCount = () => {
    if (particleCount) return particleCount;
    
    switch (size) {
      case 'sm': return 8;
      case 'md': return 12;
      case 'lg': return 16;
      case 'xl': return 24;
      case 'massive': return 32;
      default: return 12;
    }
  };

  const particles = getParticleCount();

  // Start explosion
  const explode = () => {
    if (isExploding) return;
    
    setIsExploding(true);
    setIsComplete(false);

    // Complete explosion after duration
    setTimeout(() => {
      setIsComplete(true);
      onComplete();
    }, duration);
  };

  // Auto-start if enabled
  useEffect(() => {
    if (autoStart) {
      explode();
    }
  }, [autoStart]);

  // Build CSS classes
  const explosionClasses = [
    'explosion',
    `explosion-${type}`,
    `explosion-${size}`,
    `explosion-${color}`,
    isExploding && 'explosion-active',
    isComplete && 'explosion-complete',
    className
  ].filter(Boolean).join(' ');

  // Generate particles array
  const particleElements = Array.from({ length: particles }, (_, i) => (
    <div
      key={i}
      className={`explosion-particle particle-${i + 1}`}
      style={{
        '--particle-index': i,
        '--total-particles': particles,
        '--particle-angle': `${(360 / particles) * i}deg`,
      }}
    />
  ));

  return (
    <div
      className={explosionClasses}
      style={{
        '--explosion-duration': `${duration}ms`,
        ...style
      }}
      {...rest}
    >
      {/* Core flash effect */}
      <div className="explosion-flash" />
      
      {/* Ring shockwave */}
      <div className="explosion-shockwave" />
      
      {/* Particle system */}
      <div className="explosion-particles">
        {particleElements}
      </div>
      
      {/* Secondary effects based on type */}
      {type === 'sparkle' && (
        <div className="explosion-sparkles">
          {Array.from({ length: 6 }, (_, i) => (
            <div key={i} className={`sparkle sparkle-${i + 1}`} />
          ))}
        </div>
      )}
      
      {type === 'fire' && (
        <div className="explosion-flames">
          {Array.from({ length: 4 }, (_, i) => (
            <div key={i} className={`flame flame-${i + 1}`} />
          ))}
        </div>
      )}
    </div>
  );
}

// Size constants
export const EXPLOSION_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl',
  MASSIVE: 'massive'
};

// Type constants
export const EXPLOSION_TYPES = {
  BURST: 'burst',        // Standard particle burst
  SPARKLE: 'sparkle',    // Magical sparkles
  FIRE: 'fire',          // Fire explosion with flames
  ICE: 'ice',            // Ice crystals shattering
  LIGHTNING: 'lightning', // Electric discharge
  MAGIC: 'magic'         // Mystical energy burst
};

// Color constants
export const EXPLOSION_COLORS = {
  PRIMARY: 'primary',
  FIRE: 'fire',
  ICE: 'ice',
  LIGHTNING: 'lightning',
  MAGIC: 'magic',
  TREASURE: 'treasure'
};

export default Explosion;