// CountBadge Component - Specialized badge for numeric indicators
// Perfect for party counts, queue sizes, ability counts, etc.
// Automatically handles formatting and state indication based on numbers

import React from 'react';
import Badge from './Badge.js';
import { IS_DEVELOPMENT } from '../../../shared/constants.js';

/**
 * Count/numeric badge with intelligent formatting and state indication
 * @param {object} props - CountBadge props
 * @param {number} props.count - Current count number
 * @param {number} props.max - Maximum count (optional, shows count/max format)
 * @param {string} props.label - Label text to show before count
 * @param {string} props.format - Format style ('fraction', 'simple', 'percentage')
 * @param {boolean} props.showIcon - Whether to show an icon
 * @param {string} props.icon - Custom icon to display
 * @param {string} props.size - Badge size (sm, md, lg)
 * @param {boolean} props.outlined - Outlined instead of filled
 * @param {string} props.warningThreshold - When to show warning (percentage like '80%' or number)
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional props passed to Badge
 * @returns {React.ReactElement} CountBadge component
 */
function CountBadge({
  count,
  max = null,
  label = null,
  format = 'simple',
  showIcon = false,
  icon = null,
  size = 'md',
  outlined = false,
  warningThreshold = null,
  className = '',
  ...rest
}) {
  
  // Validation
  if (IS_DEVELOPMENT) {
    if (typeof count !== 'number') {
      console.warn('CountBadge: count prop should be a number');
    }
    if (max !== null && typeof max !== 'number') {
      console.warn('CountBadge: max prop should be a number or null');
    }
  }

  // Determine badge variant based on count and thresholds
  const getBadgeVariant = () => {
    // If no max provided, use default styling
    if (max === null) {
      return count === 0 ? 'secondary' : 'primary';
    }

    // Calculate percentage if max is provided
    const percentage = (count / max) * 100;

    // Handle warning threshold
    if (warningThreshold) {
      const threshold = warningThreshold.endsWith('%') 
        ? parseFloat(warningThreshold) 
        : (warningThreshold / max) * 100;
      
      if (percentage >= threshold) {
        return 'warning';
      }
    }

    // Full capacity
    if (count >= max) {
      return 'success';
    }

    // Empty
    if (count === 0) {
      return 'secondary';
    }

    // Normal state
    return 'primary';
  };

  // Format the count display based on format prop
  const formatCount = () => {
    switch (format) {
      case 'fraction':
        return max !== null ? `${count}/${max}` : count;
      
      case 'percentage':
        if (max !== null) {
          const percentage = Math.round((count / max) * 100);
          return `${percentage}%`;
        }
        return `${count}%`;
      
      case 'simple':
      default:
        return count;
    }
  };

  // Build the content
  const buildContent = () => {
    const formattedCount = formatCount();
    const parts = [];

    // Add icon if specified
    if (showIcon && icon) {
      parts.push(
        <span key="icon" className="count-badge-icon" aria-hidden="true">
          {icon}
        </span>
      );
    }

    // Add label if specified
    if (label) {
      parts.push(
        <span key="label" className="count-badge-label">
          {label}:
        </span>
      );
    }

    // Add the formatted count
    parts.push(
      <span key="count" className="count-badge-number">
        {formattedCount}
      </span>
    );

    return parts;
  };

  // Build count-specific CSS classes
  const countClasses = [
    'count-badge', // Count badge specific styling
    `count-badge-format-${format}`, // Format-specific styling
    max !== null && 'count-badge-with-max', // Has maximum styling
    count === 0 && 'count-badge-empty', // Empty state styling
    max !== null && count >= max && 'count-badge-full', // Full state styling
    className
  ].filter(Boolean).join(' ');

  return (
    <Badge
      variant={getBadgeVariant()}
      size={size}
      outlined={outlined}
      className={countClasses}
      {...rest}
    >
      {buildContent()}
    </Badge>
  );
}

// Format constants for easy imports
export const COUNT_FORMATS = {
  SIMPLE: 'simple',
  FRACTION: 'fraction', 
  PERCENTAGE: 'percentage'
};

export default CountBadge;