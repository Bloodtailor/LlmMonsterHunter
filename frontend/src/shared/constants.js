// Shared Constants - Centralized constants for the entire frontend application
// Eliminates magic numbers and provides single source of truth for configuration values

export const GAME_RULES = {
  MAX_PARTY_SIZE: 4,
  MIN_PARTY_SIZE_FOR_DUNGEON: 1,
  MAX_FOLLOWING_MONSTERS: 1000, // Reasonable limit for UI performance
};

// Card sizes for monster cards and other flippable cards
export const CARD_SIZES = {
  SMALL: 'small',
  NORMAL: 'normal', 
  LARGE: 'large',
  FULL: 'full' // Added for fullscreen viewer
};

// Application States
export const APP_STATES = {
  LOADING: 'loading',
  ERROR: 'error',
  SUCCESS: 'success',
  IDLE: 'idle'
};

// Environment
export const IS_DEVELOPMENT = process.env.NODE_ENV === 'development';
export const IS_PRODUCTION = process.env.NODE_ENV === 'production';

// Add this to frontend/src/shared/constants.js

// Color themes for explosions and visual effects
export const COLOR_THEMES = {
  fire: ['red-intense', 'orange-flame', 'yellow-electric', 'orange-vibrant'],
  ice: ['blue-ice', 'blue-cool', 'white-pure', 'blue-electric'],
  electric: ['yellow-electric', 'blue-electric', 'white-pure', 'yellow-bright'],
  poison: ['green-electric', 'green-nature', 'yellow-citrus', 'green-emerald'],
  magic: ['purple-mystic', 'pink-vibrant', 'blue-electric', 'purple-cosmic'],
  rainbow: ['red-intense', 'orange-vibrant', 'yellow-bright', 'green-electric', 'blue-cool', 'purple-mystic'],
  gold: ['gold-bright', 'yellow-golden', 'orange-golden', 'yellow-bright'],
  shadow: ['gray-dark', 'black-soft', 'purple-deep', 'gray-medium']
};