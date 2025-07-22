// LoadingContainer Component - Full container loading with spinner and message
// Perfect for screen-level loading, component loading, and modal loading states
// Provides consistent loading experience with customizable messages and styling

import React from 'react';
import LoadingSpinner from './LoadingSpinner.js';
import { IS_DEVELOPMENT } from '../../../shared/constants.js';

/**
 * Container component for full loading states with spinner and message
 * @param {object} props - LoadingContainer props
 * @param {string} props.message - Loading message text
 * @param {string} props.size - Container size (sm, md, lg, full)
 * @param {boolean} props.overlay - Show as overlay over existing content
 * @param {string} props.spinnerSize - Size of the spinner (xs, sm, md, lg, xl)
 * @param {string} props.spinnerType - Type of spinner animation
 * @param {boolean} props.centered - Center the loading content
 * @param {React.ReactNode} props.children - Optional content to show below loading
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Function} props.onCancel - Optional cancel handler (shows cancel button)
 * @param {string} props.cancelText - Text for cancel button
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} LoadingContainer component
 */
function LoadingContainer({
  message = 'Loading...',
  size = 'md',
  overlay = false,
  spinnerSize = 'md',
  spinnerType = 'spin',
  centered = true,
  children = null,
  className = '',
  style = {},
  onCancel = null,
  cancelText = 'Cancel',
  ...rest
}) {
  
  // Build CSS classes based on props
  const containerClasses = [
    'loading-container', // Base container class
    `loading-container-${size}`, // Size styling
    overlay && 'loading-container-overlay', // Overlay styling
    centered && 'loading-container-centered', // Centered styling
    onCancel && 'loading-container-with-cancel', // With cancel button
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Handle cancel button click
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  // Render cancel button if handler provided
  const renderCancelButton = () => {
    if (!onCancel) return null;
    
    return (
      <button
        type="button"
        className="loading-cancel-button"
        onClick={handleCancel}
      >
        {cancelText}
      </button>
    );
  };

  // Development warnings
  if (IS_DEVELOPMENT) {
    if (!message) {
      console.warn('LoadingContainer: Consider providing a loading message for better UX');
    }
  }

  return (
    <div
      className={containerClasses}
      style={style}
      role="status"
      aria-live="polite"
      aria-label={message}
      {...rest}
    >
      <div className="loading-content">
        {/* Loading Spinner */}
        <LoadingSpinner 
          size={spinnerSize}
          type={spinnerType}
          className="loading-container-spinner"
        />
        
        {/* Loading Message */}
        {message && (
          <div className="loading-message">
            {message}
          </div>
        )}
        
        {/* Additional Content */}
        {children && (
          <div className="loading-additional-content">
            {children}
          </div>
        )}
        
        {/* Cancel Button */}
        {renderCancelButton()}
      </div>
    </div>
  );
}

// Size constants for easy imports
export const LOADING_CONTAINER_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  FULL: 'full'
};

export default LoadingContainer;