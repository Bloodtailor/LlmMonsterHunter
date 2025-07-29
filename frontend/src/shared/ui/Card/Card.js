// Card Component - Enhanced container for content grouping
// Replaces scattered card classes with consistent styling and behavior
// Perfect for content sections, stat displays, and organized layouts

import React from 'react';

/**
 * Enhanced card container component
 * @param {object} props - Card props
 * @param {React.ReactNode} props.children - Card content
 * @param {string} props.variant - Card style variant (default, outlined, elevated, flat)
 * @param {string} props.size - Card size (sm, md, lg, xl)
 * @param {string} props.padding - Padding variant (none, sm, md, lg)
 * @param {boolean} props.interactive - Make card clickable/hoverable
 * @param {Function} props.onClick - Click handler (makes card interactive)
 * @param {boolean} props.disabled - Disable card interactions
 * @param {string} props.background - Background variant (default, light, dark, transparent)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {string} props.ariaLabel - Accessibility label for interactive cards
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} Card component
 */
function Card({
  children,
  variant = 'default',
  size = 'md',
  padding = 'md',
  interactive = false,
  onClick = null,
  disabled = false,
  background = 'default',
  className = '',
  style = {},
  ariaLabel = null,
  ...rest
}) {
  
  // Build CSS classes based on props
  const cardClasses = [
    'card', // Base card class
    `card-${variant}`, // Variant styling
    `card-${size}`, // Size styling
    `card-padding-${padding}`, // Padding styling
    `card-background-${background}`, // Background styling
    (interactive || onClick) && 'card-interactive', // Interactive styling
    disabled && 'card-disabled', // Disabled styling
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Handle click events
  const handleClick = (event) => {
    if (disabled) {
      event.preventDefault();
      return;
    }
    
    if (onClick) {
      onClick(event);
    }
  };

  // Determine element type and props based on interactivity
  const isClickable = (interactive || onClick) && !disabled;
  
  const elementProps = {
    className: cardClasses,
    style,
    ...rest
  };

  // Interactive card (button element for accessibility)
  if (isClickable) {
    return (
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        aria-label={ariaLabel}
        {...elementProps}
      >
        {children}
      </button>
    );
  }

  // Non-interactive card (div element)
  return (
    <div {...elementProps}>
      {children}
    </div>
  );
}

// Variant constants for easy imports
export const CARD_VARIANTS = {
  DEFAULT: 'default',
  OUTLINED: 'outlined',
  ELEVATED: 'elevated',
  FLAT: 'flat'
};

// Size constants for easy imports
export const CARD_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl'
};

// Padding constants for easy imports
export const CARD_PADDING = {
  NONE: 'none',
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};

// Background constants for easy imports
export const CARD_BACKGROUNDS = {
  DEFAULT: 'default',
  LIGHT: 'light',
  DARK: 'dark',
  TRANSPARENT: 'transparent'
};

export default Card;