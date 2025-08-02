// useTypographyScale.js - Typography scaling system for cards
// Similar to getBadgeSize() but handles all text types with customizable scaling

import { CARD_SIZES } from '../constants/constants.js';

// Default text scaling strategies - can be overridden per card type
const DEFAULT_TEXT_SCALING = {
  // Simple one-to-one mapping: card size directly maps to text size
  title: {
    [CARD_SIZES.SM]: 'title-sm',
    [CARD_SIZES.MD]: 'title-md',
    [CARD_SIZES.LG]: 'title-lg',
    [CARD_SIZES.XL]: 'title-xl'
  },

  header: {
    [CARD_SIZES.SM]: 'header-sm',
    [CARD_SIZES.MD]: 'header-md',
    [CARD_SIZES.LG]: 'header-lg',
    [CARD_SIZES.XL]: 'header-xl'
  },
  
  subtitle: {
    [CARD_SIZES.SM]: 'subtitle-sm',
    [CARD_SIZES.MD]: 'subtitle-md',
    [CARD_SIZES.LG]: 'subtitle-lg',
    [CARD_SIZES.XL]: 'subtitle-xl'
  },
  
  body: {
    [CARD_SIZES.SM]: 'body-sm',
    [CARD_SIZES.MD]: 'body-md',
    [CARD_SIZES.LG]: 'body-lg',
    [CARD_SIZES.XL]: 'body-xl'
  },
  
  caption: {
    [CARD_SIZES.SM]: 'caption-sm',
    [CARD_SIZES.MD]: 'caption-md',
    [CARD_SIZES.LG]: 'caption-lg',
    [CARD_SIZES.XL]: 'caption-xl'
  },
  
  overlay: {
    [CARD_SIZES.SM]: 'overlay-sm',
    [CARD_SIZES.MD]: 'overlay-md',
    [CARD_SIZES.LG]: 'overlay-lg',
    [CARD_SIZES.XL]: 'overlay-xl'
  }
};

// Custom scaling strategies for different card types
const CARD_TYPE_SCALING = {
  // Monster cards - default scaling
  monster: DEFAULT_TEXT_SCALING,
  
  // Spell cards - maybe titles should be more prominent
  spell: {
    ...DEFAULT_TEXT_SCALING,
    title: {
      [CARD_SIZES.SM]: 'title-md',    // Bigger titles for spells
      [CARD_SIZES.MD]: 'title-lg',
      [CARD_SIZES.LG]: 'title-xl', 
      [CARD_SIZES.XL]: 'title-xl'     // Max out at xl
    }
  },
  
  // Item cards - maybe more conservative scaling
  item: {
    ...DEFAULT_TEXT_SCALING,
    title: {
      [CARD_SIZES.SM]: 'title-sm',    // Keep titles smaller for items
      [CARD_SIZES.MD]: 'title-sm',
      [CARD_SIZES.LG]: 'title-md',
      [CARD_SIZES.XL]: 'title-lg'
    }
  }
};

/**
 * Typography scaling hook - like getBadgeSize() but for all text types
 * @param {string} scale - Card size (sm, md, lg, xl) - optional, defaults to 'md'
 * @param {string} class - Card type (monster, spell, item, etc.) - optional, defaults to 'monster'
 * @returns {Function} getTextSize function
 */
export function useTypographyScale(scale = 'md', classType = 'monster') {
  
  // Get the scaling strategy for this card type
  const scalingStrategy = CARD_TYPE_SCALING[classType] || DEFAULT_TEXT_SCALING;
  
  /**
   * Get the appropriate text size class for this card size and text type
   * @param {string} textType - Type of text (title, header, subtitle, body, caption, overlay)
   * @returns {string} CSS class name (e.g., 'header-lg')
   */
  const getTextSize = (textType) => {
    const typeScaling = scalingStrategy[textType];
    if (!typeScaling) {
      console.warn(`Unknown text type: ${textType}. Available types:`, Object.keys(scalingStrategy));
      return 'body-md'; // fallback
    }
    
    const sizeClass = typeScaling[scale];
    if (!sizeClass) {
      console.warn(`Unknown card size: ${scale}. Available sizes:`, Object.keys(typeScaling));
      return 'body-md'; // fallback
    }
    
    return sizeClass;
  };
  
  return { getTextSize };
}

// Alternative: Direct function approach (if you prefer not using hooks)
export function getTextSize(scale, textType, classType = 'monster') {
  const scalingStrategy = CARD_TYPE_SCALING[classType] || DEFAULT_TEXT_SCALING;
  const typeScaling = scalingStrategy[textType];
  
  if (!typeScaling) return 'body-md';
  return typeScaling[scale] || 'body-md';
}