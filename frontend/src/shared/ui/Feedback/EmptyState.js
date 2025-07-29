// EmptyState Component - Consistent empty states for "no data found" situations
// Replaces scattered empty state implementations with unified design
// Perfect for empty lists, no search results, empty collections

import React from 'react';
import { IS_DEVELOPMENT } from '../../../shared/constants.js';

/**
 * EmptyState component for displaying "no data" states
 * @param {object} props - EmptyState props
 * @param {string} props.icon - Icon to display (emoji or icon class)
 * @param {string} props.title - Primary heading text
 * @param {React.ReactNode} props.message - Description message (can be string or JSX)
 * @param {React.ReactNode} props.action - Optional action button or element
 * @param {string} props.size - EmptyState size (sm, md, lg, xl)
 * @param {string} props.variant - Visual variant (default, subdued, highlighted)
 * @param {boolean} props.centered - Center align content (default: true)
 * @param {string} props.illustration - Optional illustration/image URL
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} EmptyState component
 */
function EmptyState({
  icon = '📋',
  title = 'No data found',
  message = null,
  action = null,
  size = 'md',
  variant = 'default',
  centered = true,
  illustration = null,
  className = '',
  style = {},
  ...rest
}) {
  
  // Build CSS classes based on props
  const emptyStateClasses = [
    'empty-state', // Base empty state class
    `empty-state-${size}`, // Size styling
    `empty-state-${variant}`, // Variant styling
    centered && 'empty-state-centered', // Centered styling
    illustration && 'empty-state-with-illustration', // Has illustration
    action && 'empty-state-with-action', // Has action
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Render illustration or icon
  const renderVisual = () => {
    if (illustration) {
      return (
        <div className="empty-state-illustration">
          <img 
            src={illustration} 
            alt="" 
            className="empty-state-image"
          />
        </div>
      );
    }

    if (icon) {
      return (
        <div className="empty-state-icon" aria-hidden="true">
          {icon}
        </div>
      );
    }

    return null;
  };

  // Render title
  const renderTitle = () => {
    if (!title) return null;
    
    return (
      <h3 className="empty-state-title">
        {title}
      </h3>
    );
  };

  // Render message
  const renderMessage = () => {
    if (!message) return null;
    
    return (
      <div className="empty-state-message">
        {typeof message === 'string' ? (
          <p>{message}</p>
        ) : (
          message
        )}
      </div>
    );
  };

  // Render action
  const renderAction = () => {
    if (!action) return null;
    
    return (
      <div className="empty-state-action">
        {action}
      </div>
    );
  };

  // Development warnings
  if (IS_DEVELOPMENT) {
    if (!title && !message) {
      console.warn('EmptyState: Should have either title or message for clarity');
    }
    if (!icon && !illustration) {
      console.warn('EmptyState: Consider adding an icon or illustration for better visual appeal');
    }
  }

  return (
    <div
      className={emptyStateClasses}
      style={style}
      role="status"
      aria-label={typeof title === 'string' ? title : 'Empty state'}
      {...rest}
    >
      <div className="empty-state-content">
        {renderVisual()}
        {renderTitle()}
        {renderMessage()}
        {renderAction()}
      </div>
    </div>
  );
}

// Size constants for easy imports
export const EMPTY_STATE_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl'
};

// Variant constants for easy imports
export const EMPTY_STATE_VARIANTS = {
  DEFAULT: 'default',
  SUBDUED: 'subdued',
  HIGHLIGHTED: 'highlighted'
};

// Common empty state presets for quick use
export const EMPTY_STATE_PRESETS = {
  NO_MONSTERS: {
    icon: '🏛️',
    title: 'No Monsters Found',
    message: 'Your collection is empty. Generate some monsters to get started!'
  },
  NO_PARTY: {
    icon: '👥',
    title: 'No Party Members',
    message: 'Add monsters to your party to begin your adventure.'
  },
  NO_SEARCH_RESULTS: {
    icon: '🔍',
    title: 'No Results Found',
    message: 'Try adjusting your search criteria or filters.'
  },
  NO_LOGS: {
    icon: '📋',
    title: 'No Logs Available',
    message: 'No activity logs found. Start generating content to see logs here.'
  },
  CONNECTION_ERROR: {
    icon: '🔌',
    title: 'Connection Error',
    message: 'Unable to connect to the server. Please check your connection and try again.'
  },
  LOADING_ERROR: {
    icon: '⚠️',
    title: 'Loading Failed',
    message: 'Something went wrong while loading data. Please try again.'
  },
  NO_CARD_ART: {
    icon: '🐲',
    title: 'No Card Art',
    message: null, // Remove the message for simplicity like the old one
    className: 'monster-art-placeholder'
  }
};

export default EmptyState;