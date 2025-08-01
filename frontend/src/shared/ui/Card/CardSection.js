// CardSection Component - Structured sections for Card content
// Provides consistent header, content, and footer sections within cards
// Perfect for organized layouts with proper spacing and styling

import React from 'react';
import { IS_DEVELOPMENT } from '../../constants/constants';
import './card.css';

/**
 * Card section component for structured card layouts
 * @param {object} props - CardSection props
 * @param {React.ReactNode} props.children - Section content
 * @param {string} props.type - Section type (header, content, footer, custom)
 * @param {string} props.title - Optional title for the section
 * @param {React.ReactNode} props.action - Optional action element (button, link, etc.)
 * @param {string} props.padding - Padding override (none, sm, md, lg)
 * @param {boolean} props.bordered - Add border around section
 * @param {boolean} props.highlighted - Highlight section background
 * @param {string} props.alignment - Content alignment (left, center, right)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} CardSection component
 */
function CardSection({
  children,
  type = 'content',
  title = null,
  action = null,
  padding = null,
  bordered = false,
  highlighted = false,
  alignment = 'left',
  className = '',
  style = {},
  ...rest
}) {
  
  // Build CSS classes based on props
  const sectionClasses = [
    'card-section', // Base section class
    `card-section-${type}`, // Type styling
    padding && `card-section-padding-${padding}`, // Padding override
    `card-section-align-${alignment}`, // Alignment styling
    bordered && 'card-section-bordered', // Bordered styling
    highlighted && 'card-section-highlighted', // Highlighted styling
    (title || action) && 'card-section-with-header', // Has header elements
    className // Additional classes
  ].filter(Boolean).join(' ');

  // Render section header (title + action)
  const renderSectionHeader = () => {
    if (!title && !action) return null;
    
    return (
      <div className="card-section-header">
        {title && (
          <div className="card-section-title">
            {typeof title === 'string' ? (
              <h4>{title}</h4>
            ) : (
              title
            )}
          </div>
        )}
        {action && (
          <div className="card-section-action">
            {action}
          </div>
        )}
      </div>
    );
  };

  // Render section content
  const renderSectionContent = () => {
    if (!children) return null;
    
    return (
      <div className="card-section-content">
        {children}
      </div>
    );
  };

  // Development warnings
  if (IS_DEVELOPMENT) {
    if (!children && !title) {
      console.warn('CardSection: Section should have either content or title');
    }
    if (type === 'header' && !title) {
      console.warn('CardSection: Header section should typically have a title');
    }
  }

  return (
    <div
      className={sectionClasses}
      style={style}
      {...rest}
    >
      {renderSectionHeader()}
      {renderSectionContent()}
    </div>
  );
}

// Section type constants for easy imports
export const CARD_SECTION_TYPES = {
  HEADER: 'header',
  CONTENT: 'content',
  FOOTER: 'footer',
  CUSTOM: 'custom'
};

// Alignment constants for easy imports
export const CARD_SECTION_ALIGNMENT = {
  LEFT: 'left',
  CENTER: 'center',
  RIGHT: 'right'
};

export default CardSection;