// ExplosionEngine.js - Raw explosion engine with full granular control
// All parameters are optional - unspecified params get randomized
// This is the core rendering engine used by ExplosionPreset

import React, { useEffect, useState } from 'react';
import { 
  SIZE_MULTIPLIERS, 
  EXPLOSION_PATTERNS, 
  ENGINE_DEFAULTS, 
  RANDOMIZATION_RANGES 
} from './ExplosionConstants.js';
import './Explosion.css';

/**
 * Raw explosion engine with full granular control
 * @param {number} props.particles - Number of main particles (0-50, randomized if not provided)
 * @param {number} props.streaks - Number of streak trails (0-30, randomized if not provided)
 * @param {number} props.rings - Number of expanding rings (0-15, randomized if not provided)
 * @param {number} props.fragments - Number of angular fragments (0-30, randomized if not provided)
 * @param {number} props.waves - Number of energy waves (0-12, randomized if not provided)
 * @param {number} props.sparks - Number of sparks (0-40, randomized if not provided)
 * @param {string} props.pattern - Movement pattern: 'radial', 'lightning', 'implosion', 'spiral', 'dome', 'chain', 'shockwave', 'shatter'
 * @param {boolean} props.hasFlash - Show center flash effect
 * @param {boolean} props.hasShockwave - Show shockwave ring
 * @param {Array} props.colors - Array of hex colors ['#ff0000', '#00ff00'] (randomized if not provided)
 * @param {string} props.size - Size: 'sm', 'md', 'lg', 'xl', 'massive'
 * @param {number} props.intensity - Intensity multiplier (0.5-3)
 * @param {number} props.speed - Speed multiplier (0.5-3)
 * @param {number} props.duration - Duration in ms (default: 1800)
 * @param {Function} props.onComplete - Callback when finished
 * @param {boolean} props.autoStart - Start immediately (default: true)
 */
function ExplosionEngine({
  particles = null,
  streaks = null,
  rings = null,
  fragments = null,
  waves = null,
  sparks = null,
  pattern = null,
  hasFlash = null,
  hasShockwave = null,
  colors = null,
  size = 'md',
  intensity = 1,
  speed = 1,
  duration = 1800,
  onComplete = () => {},
  autoStart = true,
  className = '',
  style = {},
  ...rest
}) {
  const [isActive, setIsActive] = useState(false);
  const [finalConfig, setFinalConfig] = useState(null);

  // Generate random value within range
  const randomInRange = (range) => {
    return Math.floor(Math.random() * (range.max - range.min + 1)) + range.min;
  };

  // Generate random colors
  const generateRandomColors = () => {
    const colorOptions = [
      '#ff6b35', '#f7931e', '#ffd700', '#32cd32', '#1e90ff', 
      '#9370db', '#ff1493', '#00ced1', '#ff4500', '#7fff00',
      '#dc143c', '#00bfff', '#ba55d3', '#ff6347', '#adff2f'
    ];
    const count = 2 + Math.floor(Math.random() * 3); // 2-4 colors
    const shuffled = [...colorOptions].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
  };

  // Generate final configuration with randomization
  const generateFinalConfig = () => {
    const patterns = Object.values(EXPLOSION_PATTERNS);
    
    return {
      particles: particles !== null ? particles : randomInRange(RANDOMIZATION_RANGES.particles),
      streaks: streaks !== null ? streaks : randomInRange(RANDOMIZATION_RANGES.streaks),
      rings: rings !== null ? rings : randomInRange(RANDOMIZATION_RANGES.rings),
      fragments: fragments !== null ? fragments : randomInRange(RANDOMIZATION_RANGES.fragments),
      waves: waves !== null ? waves : randomInRange(RANDOMIZATION_RANGES.waves),
      sparks: sparks !== null ? sparks : randomInRange(RANDOMIZATION_RANGES.sparks),
      pattern: pattern || patterns[Math.floor(Math.random() * patterns.length)],
      hasFlash: hasFlash !== null ? hasFlash : Math.random() > 0.3,
      hasShockwave: hasShockwave !== null ? hasShockwave : Math.random() > 0.4,
      colors: colors || generateRandomColors(),
      size,
      intensity: intensity + (Math.random() - 0.5) * 0.3, // Small random variation
      speed: speed + (Math.random() - 0.5) * 0.2,
      duration
    };
  };

  const config = finalConfig || generateFinalConfig();
  const sizeMultiplier = SIZE_MULTIPLIERS[config.size] || 1;

  const explode = () => {
    if (!finalConfig) {
      setFinalConfig(generateFinalConfig());
    }
    
    setIsActive(true);
    
    const actualDuration = config.duration / config.speed;
    setTimeout(() => {
      setIsActive(false);
      onComplete();
    }, actualDuration);
  };

  useEffect(() => {
    if (autoStart) {
      explode();
    }
  }, [autoStart]);

  const classes = [
    'ultimate-explosion',
    `explosion-${config.pattern}`,
    `explosion-${config.size}`,
    isActive && 'explosion-active',
    className
  ].filter(Boolean).join(' ');

  const actualDuration = config.duration / config.speed;
  const finalIntensity = config.intensity * sizeMultiplier;

  return (
    <div
      className={classes}
      style={{
        '--explosion-duration': `${actualDuration}ms`,
        '--explosion-intensity': finalIntensity,
        '--size-multiplier': sizeMultiplier,
        '--color-primary': config.colors[0],
        '--color-secondary': config.colors[1] || config.colors[0],
        '--color-tertiary': config.colors[2] || config.colors[0],
        '--color-accent': config.colors[3] || config.colors[0],
        ...style
      }}
      {...rest}
    >
      {/* CENTER FLASH */}
      {config.hasFlash && (
        <div className="explosion-flash" />
      )}

      {/* SHOCKWAVE */}
      {config.hasShockwave && (
        <div className="explosion-shockwave" />
      )}

      {/* PARTICLES */}
      {config.particles > 0 && (
        <div className="particle-layer">
          {Array.from({ length: Math.floor(config.particles * finalIntensity) }, (_, i) => (
            <div
              key={`particle-${i}`}
              className="explosion-particle"
              style={{
                '--element-index': i,
                '--total-elements': Math.floor(config.particles * finalIntensity),
                '--element-color': config.colors[i % config.colors.length],
                '--delay': `${(i % 6) * 30}ms`,
              }}
            />
          ))}
        </div>
      )}

      {/* STREAKS */}
      {config.streaks > 0 && (
        <div className="streak-layer">
          {Array.from({ length: Math.floor(config.streaks * finalIntensity) }, (_, i) => (
            <div
              key={`streak-${i}`}
              className="explosion-streak"
              style={{
                '--element-index': i,
                '--total-elements': Math.floor(config.streaks * finalIntensity),
                '--element-color': config.colors[i % config.colors.length],
                '--delay': `${(i % 4) * 25}ms`,
              }}
            />
          ))}
        </div>
      )}

      {/* RINGS */}
      {config.rings > 0 && (
        <div className="ring-layer">
          {Array.from({ length: config.rings }, (_, i) => (
            <div
              key={`ring-${i}`}
              className="explosion-ring"
              style={{
                '--element-index': i,
                '--total-elements': config.rings,
                '--element-color': config.colors[i % config.colors.length],
                '--delay': `${i * 100}ms`,
              }}
            />
          ))}
        </div>
      )}

      {/* FRAGMENTS */}
      {config.fragments > 0 && (
        <div className="fragment-layer">
          {Array.from({ length: Math.floor(config.fragments * finalIntensity) }, (_, i) => (
            <div
              key={`fragment-${i}`}
              className="explosion-fragment"
              style={{
                '--element-index': i,
                '--total-elements': Math.floor(config.fragments * finalIntensity),
                '--element-color': config.colors[i % config.colors.length],
                '--delay': `${(i % 5) * 20}ms`,
              }}
            />
          ))}
        </div>
      )}

      {/* WAVES */}
      {config.waves > 0 && (
        <div className="wave-layer">
          {Array.from({ length: config.waves }, (_, i) => (
            <div
              key={`wave-${i}`}
              className="explosion-wave"
              style={{
                '--element-index': i,
                '--total-elements': config.waves,
                '--element-color': config.colors[i % config.colors.length],
                '--delay': `${i * 80}ms`,
              }}
            />
          ))}
        </div>
      )}

      {/* SPARKS */}
      {config.sparks > 0 && (
        <div className="spark-layer">
          {Array.from({ length: Math.floor(config.sparks * finalIntensity) }, (_, i) => (
            <div
              key={`spark-${i}`}
              className="explosion-spark"
              style={{
                '--element-index': i,
                '--total-elements': Math.floor(config.sparks * finalIntensity),
                '--element-color': config.colors[i % config.colors.length],
                '--delay': `${Math.random() * 200}ms`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default ExplosionEngine;