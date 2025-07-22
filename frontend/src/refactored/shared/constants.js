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
  FULLSCREEN: 'fullscreen'
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