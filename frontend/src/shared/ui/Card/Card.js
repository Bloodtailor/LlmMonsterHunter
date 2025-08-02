// Card Component - Enhanced container for content grouping
// Replaces scattered card classes with consistent styling and behavior
// Perfect for content sections, stat displays, and organized layouts

import React from 'react';
import { CARD_SIZES } from '../../constants/constants.js';
import './card.css';

/**
 * Enhanced card container component
 * @param {object} props - Card props
 * @param {React.ReactNode} props.children - Card content
 * @param {string} props.variant - Card style variant (default, outlined, elevated, flat)
 * @param {string} props.size - Card size (sm, md, lg, xl) - used for sizing and CardSection typography
 * @param {boolean} props.fullWidth - Make card span full width of container (overrides size max-width)
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
  fullWidth = false,
  padding = null, // Will auto-set based on size if not provided
  interactive = false,
  onClick = null,
  disabled = false,
  background = 'default',
  className = '',
  style = {},
  ariaLabel = null,
  ...rest
}) {
  
  // Auto-set padding based on card size if not specified
  const effectivePadding = padding || size;
  
  // Build CSS classes based on props
  const cardClasses = [
    'card', // Base card class
    `card-${variant}`, // Variant styling
    !fullWidth && `card-${size}`, // Size styling (skip if fullWidth)
    `card-padding-${effectivePadding}`, // Padding styling (auto or manual)
    `card-background-${background}`, // Background styling
    (interactive || onClick) && 'card-interactive', // Interactive styling
    disabled && 'card-disabled', // Disabled styling
    fullWidth && 'card-full-width', // Full width styling
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
  
  // Enhanced children to pass size prop to CardSections
  const enhancedChildren = React.Children.map(children, (child) => {
    // Pass size prop to CardSection components for typography scaling
    if (React.isValidElement(child) && child.type?.name === 'CardSection') {
      return React.cloneElement(child, {
        size: child.props.size || size, // Allow CardSection to override size if needed
        ...child.props
      });
    }
    return child;
  });

  // Render as button if clickable, div otherwise
  if (isClickable) {
    return (
      <button
        type="button"
        className={cardClasses}
        style={style}
        onClick={handleClick}
        disabled={disabled}
        aria-label={ariaLabel}
        {...rest}
      >
        {enhancedChildren}
      </button>
    );
  }

  return (
    <div
      className={cardClasses}
      style={style}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick(e);
        }
      } : undefined}
      aria-label={ariaLabel}
      {...rest}
    >
      {enhancedChildren}
    </div>
  );
}

// Card variant constants for easy imports
export const CARD_VARIANTS = {
  DEFAULT: 'default',
  OUTLINED: 'outlined', 
  ELEVATED: 'elevated',
  FLAT: 'flat'
};

// Card padding constants for easy imports
export const CARD_PADDING = {
  NONE: 'none',
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl' // Added XL to match CARD_SIZES
};

// Card background constants for easy imports
export const CARD_BACKGROUNDS = {
  DEFAULT: 'default',
  LIGHT: 'light',
  DARK: 'dark',
  TRANSPARENT: 'transparent'
};

export default Card;