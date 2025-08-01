// Button Component - Foundation UI primitive for all button interactions
// Provides consistent styling, states, and behavior across the entire application
// Replaces scattered btn classes with a clean, reusable API

import React from 'react';
import { IS_DEVELOPMENT } from '../../constants/constants.js';
import './button.css';

/**
 * Primary Button component with variants, sizes, and states
 * @param {object} props - Button props
 * @param {React.ReactNode} props.children - Button content
 * @param {string} props.variant - Button style variant
 * @param {string} props.size - Button size
 * @param {boolean} props.loading - Show loading state
 * @param {boolean} props.disabled - Disable button
 * @param {string} props.icon - Icon to display (emoji or icon class)
 * @param {string} props.iconPosition - Icon position ('left' or 'right')
 * @param {Function} props.onClick - Click handler
 * @param {string} props.type - Button type ('button', 'submit', 'reset')
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {string} props.ariaLabel - Accessibility label
 * @param {object} props.rest - Additional HTML button attributes
 * @returns {React.ReactElement} Button component
 */
function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon = null,
  iconPosition = 'left',
  onClick = null,
  type = 'button',
  className = '',
  style = {},
  ariaLabel = null,
  ...rest
}) {
  
  // Build CSS classes based on props
  const buttonClasses = [
    'btn', // Base button class
    `btn-${variant}`, // Variant styling
    `btn-${size}`, // Size styling
    loading && 'btn-loading', // Loading state
    disabled && 'btn-disabled', // Disabled state
    icon && !children && 'btn-icon-only', // Icon-only styling
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Handle click events (prevent when loading or disabled)
  const handleClick = (event) => {
    if (loading || disabled) {
      event.preventDefault();
      return;
    }
    
    if (onClick) {
      onClick(event);
    }
  };

  // Render icon element
  const renderIcon = (iconContent) => {
    if (!iconContent) return null;
    
    return (
      <span className="btn-icon" aria-hidden="true">
        {iconContent}
      </span>
    );
  };

  // Render loading spinner
  const renderLoadingSpinner = () => {
    if (!loading) return null;
    
    return (
      <span className="btn-loading-spinner" aria-hidden="true">
        🔄
      </span>
    );
  };

  // Determine what content to show
  const getButtonContent = () => {
    if (loading) {
      return (
        <>
          {renderLoadingSpinner()}
          {children && <span className="btn-loading-text">{children}</span>}
        </>
      );
    }

    // Icon-only button
    if (icon && !children) {
      return renderIcon(icon);
    }

    // Button with icon and text
    if (icon && children) {
      return iconPosition === 'left' ? (
        <>
          {renderIcon(icon)}
          <span className="btn-text">{children}</span>
        </>
      ) : (
        <>
          <span className="btn-text">{children}</span>
          {renderIcon(icon)}
        </>
      );
    }

    // Text-only button
    return <span className="btn-text">{children}</span>;
  };

  // Development warnings
  if (IS_DEVELOPMENT) {
    if (!children && !icon) {
      console.warn('Button: Button should have either children or icon prop');
    }
    if (loading && !children) {
      console.warn('Button: Loading state should have text to show what is loading');
    }
  }

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={handleClick}
      disabled={disabled || loading}
      style={style}
      aria-label={ariaLabel || (icon && !children ? 'Button' : undefined)}
      aria-busy={loading}
      {...rest}
    >
      {getButtonContent()}
    </button>
  );
}

// Variant constants for easy imports
export const BUTTON_VARIANTS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary', 
  DANGER: 'danger',
  SUCCESS: 'success',
  WARNING: 'warning',
  GHOST: 'ghost',
  LINK: 'link'
};

// Size constants for easy imports
export const BUTTON_SIZES = {
  SM: 'sm',
  MD: 'md', 
  LG: 'lg',
  XL: 'xl'
};

export default Button;