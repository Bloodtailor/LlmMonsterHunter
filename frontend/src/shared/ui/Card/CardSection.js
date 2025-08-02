// CardSection Component - Simplified structure
// Clear pattern: Header(title) → Content(optional title) → Footer(no title)
// Typography: Header titles use 'title', Content titles use 'header'

import React from 'react';
import { IS_DEVELOPMENT } from '../../constants/constants';
import { useTypographyScale } from '../../hooks/useTypographyScale';
import './cardSection.css';

/**
 * Simplified CardSection component with clear usage patterns
 * @param {object} props - CardSection props
 * @param {React.ReactNode} props.children - Section content
 * @param {string} props.type - Section type (header, content, footer)
 * @param {string} props.size - Section size for spacing (sm, md, lg, xl) - defaults to 'md'
 * @param {string} props.title - Title text (required for header, optional for content, forbidden for footer)
 * @param {React.ReactNode} props.action - Optional action element (button, link, etc.)
 * @param {string} props.classType - Optional card class type for typography scaling
 * @param {boolean} props.bordered - Add debug border (development only)
 * @param {boolean} props.highlighted - Add debug highlight (development only)
 * @param {string} props.alignment - Content alignment (left, center, right)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} CardSection component
 */
function CardSection({
  children,
  type = 'content',
  size = 'md',
  title = null,
  action = null,
  classType = undefined,
  bordered = false,
  highlighted = false,
  alignment = 'left',
  className = '',
  style = {},
  ...rest
}) {
  
  // Get typography scaling
  const { getTextSize } = useTypographyScale(size, classType);
  
  // Development warnings for proper usage
  if (IS_DEVELOPMENT) {
    if (type === 'header' && !title) {
      console.warn('CardSection: Header sections must have a title');
    }
    if (type === 'footer' && title) {
      console.warn('CardSection: Footer sections should not have titles');
    }
    if (!children && !title) {
      console.warn('CardSection: Section should have either content or title');
    }
  }

  // Determine typography for titles based on section type
  const getTitleTypography = () => {
    switch (type) {
      case 'header': return 'title';   // Header titles use title typography
      case 'content': return 'header'; // Content titles use header typography  
      case 'footer': return null;      // Footer never has titles
      default: return 'header';
    }
  };

  // Build CSS classes
  const sectionClasses = [
    'card-section',
    `card-section-${size}`,
    `card-section-${type}`,
    `card-section-align-${alignment}`,
    // Add has-title class for content sections with titles (affects spacing)
    type === 'content' && title && 'card-section-has-title',
    bordered && 'card-section-bordered',
    highlighted && 'card-section-highlighted',
    className
  ].filter(Boolean).join(' ');

  // Render title + action (if any)
  const renderTitleArea = () => {
    if (!title && !action) return null;
    
    // Footer should never render title area
    if (type === 'footer') return null;
    
    const titleTypography = getTitleTypography();
    
    return (
      <div className="card-section-title-container">
        {title && (
          <div className="card-section-title">
            {typeof title === 'string' ? (
              <h4 className={getTextSize(titleTypography)}>{title}</h4>
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

  // Render content area
  const renderContentArea = () => {
    if (!children) return null;
    
    return (
      <div className="card-section-content-area">
        {children}
      </div>
    );
  };

  return (
    <div
      className={sectionClasses}
      style={style}
      {...rest}
    >
      {renderTitleArea()}
      {renderContentArea()}
    </div>
  );
}

// Section type constants
export const CARD_SECTION_TYPES = {
  HEADER: 'header',
  CONTENT: 'content', 
  FOOTER: 'footer'
};

// Alignment constants
export const CARD_SECTION_ALIGNMENT = {
  LEFT: 'left',
  CENTER: 'center',
  RIGHT: 'right'
};

export default CardSection;