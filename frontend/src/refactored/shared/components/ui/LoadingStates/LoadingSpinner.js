// LoadingSpinner Component - Basic loading spinner for any loading state
// Provides consistent spinner styling and animations across the application
// Perfect for buttons, inline loading, and small loading indicators

import React from 'react';

/**
 * Basic loading spinner component with size and animation variants
 * @param {object} props - LoadingSpinner props
 * @param {string} props.size - Spinner size (xs, sm, md, lg, xl)
 * @param {string} props.color - Color variant (primary, secondary, light, dark)
 * @param {string} props.type - Animation type (spin, pulse, bounce, dots)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {string} props.ariaLabel - Accessibility label
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} LoadingSpinner component
 */
function LoadingSpinner({
  size = 'md',
  color = 'primary',
  type = 'spin',
  className = '',
  style = {},
  ariaLabel = 'Loading',
  ...rest
}) {
  
  // Build CSS classes based on props
  const spinnerClasses = [
    'loading-spinner', // Base spinner class
    `loading-spinner-${size}`, // Size styling
    `loading-spinner-${color}`, // Color styling
    `loading-spinner-${type}`, // Animation type
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Get spinner content based on type
  const getSpinnerContent = () => {
    switch (type) {
      case 'spin':
        return '🔄'; // Spinning arrow/circle
      
      case 'pulse':
        return '⭕'; // Pulsing circle
      
      case 'bounce':
        return '⚡'; // Bouncing element
      
      case 'dots':
        return (
          <span className="loading-dots-container">
            <span className="loading-dot">•</span>
            <span className="loading-dot">•</span>
            <span className="loading-dot">•</span>
          </span>
        );
      
      case 'bars':
        return (
          <span className="loading-bars-container">
            <span className="loading-bar"></span>
            <span className="loading-bar"></span>
            <span className="loading-bar"></span>
          </span>
        );
      
      default:
        return '🔄';
    }
  };

  return (
    <div
      className={spinnerClasses}
      style={style}
      role="status"
      aria-label={ariaLabel}
      aria-live="polite"
      {...rest}
    >
      {getSpinnerContent()}
    </div>
  );
}

// Size constants for easy imports
export const LOADING_SIZES = {
  XS: 'xs',
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl'
};

// Color constants for easy imports
export const LOADING_COLORS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  LIGHT: 'light',
  DARK: 'dark',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error'
};

// Animation type constants for easy imports
export const LOADING_TYPES = {
  SPIN: 'spin',
  PULSE: 'pulse',
  BOUNCE: 'bounce',
  DOTS: 'dots',
  BARS: 'bars'
};

export default LoadingSpinner;