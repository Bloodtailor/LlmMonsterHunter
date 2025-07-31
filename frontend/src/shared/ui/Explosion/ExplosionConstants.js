// ExplosionConstants.js - All explosion-related constants
// Centralized configuration for the explosion system

// Explosion type identifiers
export const EXPLOSION_TYPES = {
  PARTICLE_STORM: 'particle-storm',
  LIGHTNING_CRACK: 'lightning-crack',
  GRAVITY_IMPLOSION: 'gravity-implosion',
  PLASMA_VORTEX: 'plasma-vortex',
  NUCLEAR_DOME: 'nuclear-dome',
  CHAIN_REACTION: 'chain-reaction',
  SHOCKWAVE_BLAST: 'shockwave-blast',
  SHATTER_BREAK: 'shatter-break'
};

// Size multipliers for explosion scaling
export const SIZE_MULTIPLIERS = {
  sm: 0.6,
  md: 1.0,
  lg: 1.4,
  xl: 1.8,
  massive: 2.5
};

// Explosion type configurations - defines how each preset explosion works
export const EXPLOSION_CONFIGS = {
  'particle-storm': {
    particles: 45,
    streaks: 20,
    rings: 3,
    fragments: 0,
    waves: 0,
    sparks: 25,
    pattern: 'radial',
    hasFlash: true,
    hasShockwave: true
  },
  'lightning-crack': {
    particles: 5,
    streaks: 12,
    rings: 1,
    fragments: 0,
    waves: 0,
    sparks: 30,
    pattern: 'lightning',
    hasFlash: true,
    hasShockwave: false
  },
  'gravity-implosion': {
    particles: 30,
    streaks: 8,
    rings: 5,
    fragments: 0,
    waves: 3,
    sparks: 15,
    pattern: 'implosion',
    hasFlash: true,
    hasShockwave: true
  },
  'plasma-vortex': {
    particles: 35,
    streaks: 15,
    rings: 2,
    fragments: 0,
    waves: 6,
    sparks: 20,
    pattern: 'spiral',
    hasFlash: false,
    hasShockwave: false
  },
  'nuclear-dome': {
    particles: 20,
    streaks: 5,
    rings: 8,
    fragments: 0,
    waves: 10,
    sparks: 10,
    pattern: 'dome',
    hasFlash: true,
    hasShockwave: true
  },
  'chain-reaction': {
    particles: 25,
    streaks: 10,
    rings: 6,
    fragments: 0,
    waves: 4,
    sparks: 35,
    pattern: 'chain',
    hasFlash: true,
    hasShockwave: false
  },
  'shockwave-blast': {
    particles: 15,
    streaks: 8,
    rings: 12,
    fragments: 0,
    waves: 15,
    sparks: 5,
    pattern: 'shockwave',
    hasFlash: true,
    hasShockwave: true
  },
  'shatter-break': {
    particles: 10,
    streaks: 5,
    rings: 2,
    fragments: 25,
    waves: 0,
    sparks: 15,
    pattern: 'shatter',
    hasFlash: true,
    hasShockwave: false
  }
};

// Pattern identifiers for different movement types
export const EXPLOSION_PATTERNS = {
  RADIAL: 'radial',
  LIGHTNING: 'lightning', 
  IMPLOSION: 'implosion',
  SPIRAL: 'spiral',
  DOME: 'dome',
  CHAIN: 'chain',
  SHOCKWAVE: 'shockwave',
  SHATTER: 'shatter'
};

// Default values for ExplosionEngine
export const ENGINE_DEFAULTS = {
  particles: 16,
  streaks: 8,
  rings: 2,
  fragments: 0,
  waves: 2,
  sparks: 10,
  pattern: 'radial',
  hasFlash: true,
  hasShockwave: true,
  size: 'md',
  intensity: 1,
  speed: 1,
  duration: 1800
};

// Randomization ranges for ExplosionEngine
export const RANDOMIZATION_RANGES = {
  particles: { min: 5, max: 50 },
  streaks: { min: 0, max: 30 },
  rings: { min: 0, max: 15 },
  fragments: { min: 0, max: 30 },
  waves: { min: 0, max: 12 },
  sparks: { min: 0, max: 40 },
  intensity: { min: 0.5, max: 2.5 },
  speed: { min: 0.6, max: 2.8 }
};

export default {
  EXPLOSION_TYPES,
  SIZE_MULTIPLIERS,
  EXPLOSION_CONFIGS,
  EXPLOSION_PATTERNS,
  ENGINE_DEFAULTS,
  RANDOMIZATION_RANGES
};