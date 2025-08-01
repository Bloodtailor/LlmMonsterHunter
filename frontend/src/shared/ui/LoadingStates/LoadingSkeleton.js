import React from 'react';
import './loading.css';

/**
 * Minimal Skeleton placeholder component for loading content
 * @param {string} type - 'monsterCard' | 'text'
 * @param {number} count - Number of skeletons to render
 * @param {boolean} animated - Enable shimmer animation
 * @param {object} style - Optional inline styles
 * @returns {React.ReactElement}
 */
function LoadingSkeleton({
  type = 'text',
  count = 1,
  animated = true,
  style = {},
}) {
  const skeletonClass = `loading-skeleton ${animated ? 'animated' : ''}`;

  const renderMonsterCard = () => (
    <div className={`${skeletonClass} monster-card-skeleton`} style={style}>
      <div className="skeleton-image" />
      <div className="skeleton-title" />
      <div className="skeleton-line" />
      <div className="skeleton-line" />
    </div>
  );

  const renderText = () => (
    <div className={`${skeletonClass} text-skeleton`} style={style} />
  );

  const renderOne = (index) => {
    switch (type) {
      case 'monsterCard':
        return <div key={index}>{renderMonsterCard()}</div>;
      case 'text':
      default:
        return <div key={index}>{renderText()}</div>;
    }
  };

  return (
    <div className="loading-skeleton-wrapper">
      {Array.from({ length: count }).map((_, i) => renderOne(i))}
    </div>
  );
}

export default LoadingSkeleton;
