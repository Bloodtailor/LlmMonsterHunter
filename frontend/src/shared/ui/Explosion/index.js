// Explosion System Exports - Modular explosion engine with presets and raw control
// Choose the right component for your needs

// Main components
export { default as ExplosionEngine } from './ExplosionEngine.js';     // Raw granular control
export { default as ExplosionPreset } from './ExplosionPreset.js';     // High-level presets
export { default as Explosion } from './ExplosionPreset.js';           // Default to preset version

// Constants
export { 
  EXPLOSION_TYPES, 
  EXPLOSION_PATTERNS, 
  SIZE_MULTIPLIERS,
  EXPLOSION_CONFIGS,
  ENGINE_DEFAULTS,
  RANDOMIZATION_RANGES
} from './ExplosionConstants.js';

// For backwards compatibility - default export is the preset version
export { default } from './ExplosionPreset.js';