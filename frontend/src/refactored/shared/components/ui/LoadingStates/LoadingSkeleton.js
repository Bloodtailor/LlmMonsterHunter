// LoadingSkeleton Component - Placeholder shapes while content loads
// Provides better UX than spinners by showing the shape of content that will appear
// Perfect for monster cards, list items, and any predictable content layout

import React from 'react';

/**
 * Skeleton placeholder component for content loading states
 * @param {object} props - LoadingSkeleton props
 * @param {string} props.type - Predefined skeleton type (monsterCard, listItem, text, button, etc.)
 * @param {number} props.count - Number of skeleton items to render
 * @param {boolean} props.animated - Enable subtle shimmer animation
 * @param {number} props.width - Custom width (overrides type default)
 * @param {number} props.height - Custom height (overrides type default)
 * @param {string} props.shape - Shape variant (rectangle, circle, rounded)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} LoadingSkeleton component
 */
function LoadingSkeleton({
  type = 'text',
  count = 1,
  animated = true,
  width = null,
  height = null,
  shape = 'rectangle',
  className = '',
  style = {},
  ...rest
}) {
  
  // Predefined skeleton types with their default dimensions and layout
  const skeletonTypes = {
    monsterCard: {
      width: '280px',
      height: '400px',
      shape: 'rounded',
      layout: 'card'
    },
    listItem: {
      width: '100%',
      height: '60px',
      shape: 'rounded',
      layout: 'horizontal'
    },
    text: {
      width: '100%',
      height: '1rem',
      shape: 'rectangle',
      layout: 'simple'
    },
    textBlock: {
      width: '100%',
      height: '4rem',
      shape: 'rectangle',
      layout: 'simple'
    },
    button: {
      width: '120px',
      height: '40px',
      shape: 'rounded',
      layout: 'simple'
    },
    avatar: {
      width: '40px',
      height: '40px',
      shape: 'circle',
      layout: 'simple'
    },
    badge: {
      width: '80px',
      height: '24px',
      shape: 'rounded',
      layout: 'simple'
    }
  };

  // Get type configuration
  const typeConfig = skeletonTypes[type] || skeletonTypes.text;
  
  // Build CSS classes based on props
  const skeletonClasses = [
    'loading-skeleton', // Base skeleton class
    `loading-skeleton-${type}`, // Type-specific styling
    `loading-skeleton-${shape || typeConfig.shape}`, // Shape styling
    `loading-skeleton-layout-${typeConfig.layout}`, // Layout styling
    animated && 'loading-skeleton-animated', // Animation styling
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Build style object with dimensions
  const skeletonStyle = {
    width: width || typeConfig.width,
    height: height || typeConfig.height,
    ...style
  };

  // Render complex skeleton layouts
  const renderComplexSkeleton = () => {
    if (typeConfig.layout === 'card') {
      return (
        <div className="loading-skeleton-card-layout">
          {/* Card image area */}
          <div className="loading-skeleton-card-image" />
          
          {/* Card content area */}
          <div className="loading-skeleton-card-content">
            <div className="loading-skeleton-card-title" />
            <div className="loading-skeleton-card-subtitle" />
            <div className="loading-skeleton-card-text-line" />
            <div className="loading-skeleton-card-text-line" />
          </div>
        </div>
      );
    }

    if (typeConfig.layout === 'horizontal') {
      return (
        <div className="loading-skeleton-horizontal-layout">
          <div className="loading-skeleton-horizontal-avatar" />
          <div className="loading-skeleton-horizontal-content">
            <div className="loading-skeleton-horizontal-title" />
            <div className="loading-skeleton-horizontal-subtitle" />
          </div>
        </div>
      );
    }

    // Simple layout - just the skeleton shape
    return null;
  };

  // Render single skeleton item
  const renderSkeletonItem = (index) => {
    const complexContent = renderComplexSkeleton();
    
    return (
      <div
        key={index}
        className={skeletonClasses}
        style={skeletonStyle}
        role="status"
        aria-label="Loading content"
        {...(index === 0 ? rest : {})} // Only apply rest props to first item
      >
        {complexContent}
      </div>
    );
  };

  // Render multiple skeleton items if count > 1
  if (count > 1) {
    return (
      <div className="loading-skeleton-group">
        {Array.from({ length: count }).map((_, index) => renderSkeletonItem(index))}
      </div>
    );
  }

  // Render single skeleton item
  return renderSkeletonItem(0);
}

// Type constants for easy imports
export const SKELETON_TYPES = {
  MONSTER_CARD: 'monsterCard',
  LIST_ITEM: 'listItem',
  TEXT: 'text',
  TEXT_BLOCK: 'textBlock',
  BUTTON: 'button',
  AVATAR: 'avatar',
  BADGE: 'badge'
};

// Shape constants for easy imports
export const SKELETON_SHAPES = {
  RECTANGLE: 'rectangle',
  ROUNDED: 'rounded',
  CIRCLE: 'circle'
};

export default LoadingSkeleton;