// LoadingSpinner Component - Pure CSS loading spinners for any loading state
// Provides consistent spinner styling and animations across the application
// Perfect for buttons, inline loading, and small loading indicators

import React from 'react';
import './loading.css';

/**
 * Pure CSS loading spinner component with size and animation variants
 * @param {object} props - LoadingSpinner props
 * @param {string} props.size - Spinner size (xs, sm, md, lg, xl)
 * @param {string} props.color - Color variant (primary, secondary, light, dark)
 * @param {string} props.type - Animation type (spin, pulse, bounce, dots, bars)
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

  // Get spinner content based on type - now pure CSS
  const getSpinnerContent = () => {
    switch (type) {
      case 'spin':
        return <div className="spinner-ring" />;
      
      case 'pulse':
        return <div className="spinner-circle" />;
      
      case 'bounce':
        return <div className="spinner-bounce" />;
      
      case 'dots':
        return (
          <div className="loading-dots-container">
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
          </div>
        );
      
      case 'bars':
        return (
          <div className="loading-bars-container">
            <div className="loading-bar"></div>
            <div className="loading-bar"></div>
            <div className="loading-bar"></div>
          </div>
        );
      
      case 'cardFlip':
        return (
          <div className="spinner-card-flip">
            <div className="spinner-card-inner">
              <div className="spinner-card-front">
                <div className="card-image-area"></div>
                <div className="card-title-line"></div>
                <div className="card-text-line"></div>
                <div className="card-text-line short"></div>
              </div>
              <div className="spinner-card-back">
                <div className="card-back-pattern"></div>
              </div>
            </div>
          </div>
        );
      
      default:
        return <div className="spinner-ring" />;
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
  // Inline/proportional sizes (font-size based) - for cohesive component sizing
  XS: 'xs',
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl',
  
  // Standalone sizes (explicit sizing) - for prominent loading states
  CARD: 'card',        // ~32px - for loading individual cards
  SECTION: 'section',  // ~48px - for loading content sections  
  SCREEN: 'screen'     // ~64px - for full-screen loading
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
  BARS: 'bars',
  CARD_FLIP: 'cardFlip'  // 3D rotating monster card
};

export default LoadingSpinner;