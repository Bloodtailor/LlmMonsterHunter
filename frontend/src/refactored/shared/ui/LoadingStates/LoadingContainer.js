import React from 'react';
import LoadingSpinner from './LoadingSpinner.js';

/**
 * Simplified full-screen or inline loading container
 * @param {string} message - Text to show while loading
 * @param {boolean} overlay - If true, shows full-screen overlay
 * @param {boolean} centered - Center content (default: true)
 * @param {Function} onCancel - If provided, shows cancel button
 * @param {React.ReactNode} children - Optional extra info/content
 * @returns {React.ReactElement}
 */
function LoadingContainer({
  message = 'Loading...',
  overlay = false,
  centered = true,
  onCancel = null,
  children = null,
}) {
  const containerClasses = [
    'loading-container',
    overlay && 'loading-container-overlay',
    centered && 'loading-container-centered',
    onCancel && 'loading-container-with-cancel',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={containerClasses} role="status" aria-live="polite" aria-label={message}>
      <div className="loading-content">
        <LoadingSpinner />
        {message && <div className="loading-message">{message}</div>}
        {children && <div className="loading-extra">{children}</div>}
        {onCancel && (
          <button className="loading-cancel-button" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}

export default LoadingContainer;
