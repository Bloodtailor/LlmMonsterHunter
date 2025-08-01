// Badge Component - Foundation UI primitive for labels, tags, and indicators
// Base component for all badge variations (status, count, custom)
// Provides consistent styling and behavior for small informational elements

import React from 'react';
import { IS_DEVELOPMENT } from '../../../constants/constants.js';

/**
 * Base Badge component for labels, tags, and indicators
 * @param {object} props - Badge props
 * @param {React.ReactNode} props.children - Badge content
 * @param {string} props.variant - Badge style variant
 * @param {string} props.size - Badge size
 * @param {string} props.color - Color override (overrides variant colors)
 * @param {boolean} props.pill - Rounded pill styling
 * @param {boolean} props.outlined - Outlined instead of filled
 * @param {Function} props.onClick - Click handler (makes badge interactive)
 * @param {boolean} props.removable - Show remove button
 * @param {Function} props.onRemove - Remove button click handler
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {string} props.ariaLabel - Accessibility label
 * @param {Object} props.rest - Additional HTML span attributes
 * @returns {React.ReactElement} Badge component
 */
function Badge({
  children,
  variant = 'primary',
  size = 'md',
  color = null,
  pill = false,
  outlined = false,
  onClick = null,
  removable = false,
  onRemove = null,
  className = '',
  style = {},
  ariaLabel = null,
  ...rest
}) {
  
  // Build CSS classes based on props
  const badgeClasses = [
    'badge', // Base badge class
    `badge-${variant}`, // Variant styling
    `badge-${size}`, // Size styling
    pill && 'badge-pill', // Pill styling
    outlined && 'badge-outlined', // Outlined styling
    onClick && 'badge-interactive', // Clickable styling
    removable && 'badge-removable', // Removable styling
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Handle click events
  const handleClick = (event) => {
    if (onClick) {
      onClick(event);
    }
  };

  // Handle remove button click
  const handleRemove = (event) => {
    event.stopPropagation(); // Prevent badge click when remove is clicked
    if (onRemove) {
      onRemove(event);
    }
  };

  // Render remove button
  const renderRemoveButton = () => {
    if (!removable) return null;
    
    return (
      <button
        type="button"
        className="badge-remove-button"
        onClick={handleRemove}
        aria-label="Remove"
        tabIndex={-1} // Remove from tab order, use badge tabIndex instead
      >
        ✕
      </button>
    );
  };

  // Development warnings
  if (IS_DEVELOPMENT) {
    if (!children) {
      console.warn('Badge: Badge should have content in children prop');
    }
    if (removable && !onRemove) {
      console.warn('Badge: removable Badge should have onRemove handler');
    }
  }

  // Determine element type and props
  const elementProps = {
    className: badgeClasses,
    style: color ? { ...style, backgroundColor: color } : style,
    'aria-label': ariaLabel,
    ...rest
  };

  // Interactive badge (button element)
  if (onClick) {
    return (
      <button
        type="button"
        onClick={handleClick}
        {...elementProps}
      >
        <span className="badge-content">{children}</span>
        {renderRemoveButton()}
      </button>
    );
  }

  // Non-interactive badge (span element)
  return (
    <span {...elementProps}>
      <span className="badge-content">{children}</span>
      {renderRemoveButton()}
    </span>
  );
}

// Variant constants for easy imports
export const BADGE_VARIANTS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Size constants for easy imports
export const BADGE_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};

export default Badge;