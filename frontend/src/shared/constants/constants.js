// Shared Constants - Centralized constants for the entire frontend application
// Eliminates magic numbers and provides single source of truth for configuration values

export const GAME_RULES = {
  MAX_PARTY_SIZE: 4,
  MIN_PARTY_SIZE_FOR_DUNGEON: 1,
  MAX_FOLLOWING_MONSTERS: 1000, // Reasonable limit for UI performance
};

/// Card sizes for all card components throughout the application
// UNIFIED SYSTEM - works for both types of "cards" in this codebase:
//
// 1. GAME CARDS (primary use): MonsterCard, FlippableCard - actual playing card components
// 2. UI CARDS (secondary use): Generic UI containers (Card primitive) for content organization
//
// DESIGNED FOR: Game cards (MonsterCard, etc.) but sized appropriately for UI cards too
// REPLACES: Any component-specific sizing systems (FLIPPABLE_CARD_SIZES, etc.)
//
// USAGE:
// - Game cards: <MonsterCard size={CARD_SIZES.LG} /> 
// - UI cards: <Card size={CARD_SIZES.MD} />
// - CardSection typography scaling via formatText prop
//
// SIZE MEANINGS:
// GAME CARDS (MonsterCard, FlippableCard):
// - SM: Thumbnail/preview mode, compact grid display
// - MD: Standard card size for normal gameplay - DEFAULT  
// - LG: Detailed view, emphasized display
// - XL: Focused/fullscreen mode, primary display
//
// UI CARDS (Card primitive containers):
// - SM: Small content container
// - MD: Medium content container - DEFAULT
// - LG: Large content container  
// - XL: Extra large content container (just a really big card)
//
// NOTE: For full-width UI cards, override max-width separately while keeping 
// size family for consistent padding/margins and CardSection typography scaling
//
// TYPOGRAPHY SCALING:
// CardSection automatically scales text based on these sizes
export const CARD_SIZES = {
  SM: 'sm',
  MD: 'md', 
  LG: 'lg',
  XL: 'xl'
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