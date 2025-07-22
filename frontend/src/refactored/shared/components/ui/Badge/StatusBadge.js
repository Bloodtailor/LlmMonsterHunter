// StatusBadge Component - Specialized badge for status indicators
// Handles success, error, pending, warning states with consistent icons and colors
// Perfect for party status, generation status, API connectivity, etc.

import React from 'react';
import Badge from './Badge.js';

/**
 * Status-specific badge with predefined icons and styling
 * @param {object} props - StatusBadge props
 * @param {string} props.status - Status type (success, error, pending, warning, info)
 * @param {React.ReactNode} props.children - Status text content
 * @param {boolean} props.showIcon - Whether to show status icon (default: true)
 * @param {string} props.iconOverride - Custom icon to override default status icon
 * @param {string} props.size - Badge size (sm, md, lg)
 * @param {boolean} props.outlined - Outlined instead of filled
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional props passed to Badge
 * @returns {React.ReactElement} StatusBadge component
 */
function StatusBadge({
  status,
  children,
  showIcon = true,
  iconOverride = null,
  size = 'md',
  outlined = false,
  className = '',
  ...rest
}) {
  
  // Status configuration mapping
  const statusConfig = {
    success: {
      variant: 'success',
      icon: '✅',
      defaultText: 'Success'
    },
    error: {
      variant: 'error', 
      icon: '❌',
      defaultText: 'Error'
    },
    pending: {
      variant: 'warning',
      icon: '⏳',
      defaultText: 'Pending'
    },
    warning: {
      variant: 'warning',
      icon: '⚠️',
      defaultText: 'Warning'
    },
    info: {
      variant: 'info',
      icon: 'ℹ️',
      defaultText: 'Info'
    },
    generating: {
      variant: 'info',
      icon: '🔄',
      defaultText: 'Generating'
    },
    completed: {
      variant: 'success',
      icon: '✅',
      defaultText: 'Completed'
    },
    failed: {
      variant: 'error',
      icon: '❌', 
      defaultText: 'Failed'
    },
    ready: {
      variant: 'success',
      icon: '✅',
      defaultText: 'Ready'
    },
    loading: {
      variant: 'info',
      icon: '🔄',
      defaultText: 'Loading'
    }
  };

  // Get status configuration
  const config = statusConfig[status] || statusConfig.info;
  
  // Determine icon to display
  const icon = iconOverride || (showIcon ? config.icon : null);
  
  // Determine content to display
  const content = children || config.defaultText;
  
  // Build status-specific CSS classes
  const statusClasses = [
    'status-badge', // Status badge specific styling
    `status-badge-${status}`, // Status-specific styling
    className
  ].filter(Boolean).join(' ');

  // Render content with optional icon
  const renderContent = () => {
    if (icon && content) {
      return (
        <>
          <span className="status-badge-icon" aria-hidden="true">{icon}</span>
          <span className="status-badge-text">{content}</span>
        </>
      );
    }
    
    if (icon && !content) {
      return <span className="status-badge-icon">{icon}</span>;
    }
    
    return content;
  };

  return (
    <Badge
      variant={config.variant}
      size={size}
      outlined={outlined}
      className={statusClasses}
      {...rest}
    >
      {renderContent()}
    </Badge>
  );
}

// Status constants for easy imports and consistency
export const STATUS_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  PENDING: 'pending',
  WARNING: 'warning',
  INFO: 'info',
  GENERATING: 'generating',
  COMPLETED: 'completed',
  FAILED: 'failed',
  READY: 'ready',
  LOADING: 'loading'
};

export default StatusBadge;