// Alert Component - Standardized messages for success, error, warning, and info states
// Replaces scattered alert classes with consistent styling and behavior
// Supports closeable alerts, custom icons, and action buttons

import React from 'react';
import { IS_DEVELOPMENT } from '../../../constants/constants.js';

/**
 * Alert component for displaying important messages to users
 * @param {object} props - Alert props
 * @param {string} props.type - Alert type (success, error, warning, info, loading)
 * @param {string} props.title - Alert title (optional)
 * @param {React.ReactNode} props.children - Alert message content
 * @param {boolean} props.closeable - Show close button (default: false)
 * @param {Function} props.onClose - Close button click handler
 * @param {string} props.icon - Custom icon (overrides type default)
 * @param {boolean} props.showIcon - Whether to show icon (default: true)
 * @param {string} props.size - Alert size (sm, md, lg)
 * @param {boolean} props.outlined - Outlined instead of filled
 * @param {React.ReactNode} props.action - Optional action button/element
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} Alert component
 */
function Alert({
  type = 'info',
  title = null,
  children,
  closeable = false,
  onClose = null,
  icon = null,
  showIcon = true,
  size = 'md',
  outlined = false,
  action = null,
  className = '',
  style = {},
  ...rest
}) {
  
  // Alert type configuration
  const alertTypeConfig = {
    success: {
      variant: 'success',
      icon: '✅',
      defaultTitle: 'Success'
    },
    error: {
      variant: 'error',
      icon: '❌',
      defaultTitle: 'Error'
    },
    warning: {
      variant: 'warning',
      icon: '⚠️',
      defaultTitle: 'Warning'
    },
    info: {
      variant: 'info',
      icon: 'ℹ️',
      defaultTitle: 'Information'
    },
    loading: {
      variant: 'info',
      icon: '🔄',
      defaultTitle: 'Loading'
    }
  };

  // Get alert configuration
  const config = alertTypeConfig[type] || alertTypeConfig.info;
  
  // Build CSS classes based on props
  const alertClasses = [
    'alert', // Base alert class
    `alert-${config.variant}`, // Variant styling
    `alert-${size}`, // Size styling
    outlined && 'alert-outlined', // Outlined styling
    closeable && 'alert-closeable', // Closeable styling
    action && 'alert-with-action', // Has action styling
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Handle close button click
  const handleClose = () => {
    if (onClose) {
      onClose();
    }
  };

  // Render alert icon
  const renderIcon = () => {
    if (!showIcon) return null;
    
    const iconToShow = icon || config.icon;
    
    return (
      <div className="alert-icon" aria-hidden="true">
        {iconToShow}
      </div>
    );
  };

  // Render close button
  const renderCloseButton = () => {
    if (!closeable) return null;
    
    return (
      <button
        type="button"
        className="alert-close-button"
        onClick={handleClose}
        aria-label="Close alert"
      >
        ✕
      </button>
    );
  };

  // Render alert header (icon + title + close)
  const renderHeader = () => {
    const hasHeader = showIcon || title || closeable;
    if (!hasHeader) return null;
    
    return (
      <div className="alert-header">
        {renderIcon()}
        {title && (
          <div className="alert-title">
            {title}
          </div>
        )}
        <div className="alert-header-spacer" />
        {renderCloseButton()}
      </div>
    );
  };

  // Render alert content
  const renderContent = () => {
    if (!children) return null;
    
    return (
      <div className="alert-content">
        {children}
      </div>
    );
  };

  // Render action area
  const renderAction = () => {
    if (!action) return null;
    
    return (
      <div className="alert-action">
        {action}
      </div>
    );
  };

  // Development warnings
  if (IS_DEVELOPMENT) {
    if (!children && !title) {
      console.warn('Alert: Alert should have either title or content');
    }
    if (closeable && !onClose) {
      console.warn('Alert: Closeable alert should have onClose handler');
    }
  }

  return (
    <div
      className={alertClasses}
      style={style}
      role="alert"
      aria-live="polite"
      {...rest}
    >
      {renderHeader()}
      {renderContent()}
      {renderAction()}
    </div>
  );
}

// Alert type constants for easy imports
export const ALERT_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
  LOADING: 'loading'
};

// Alert size constants for easy imports
export const ALERT_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};

export default Alert;