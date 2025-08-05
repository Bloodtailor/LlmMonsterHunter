// Scroll Component - Simple scrollable container with custom styling
// Perfect for streaming text, queue lists, and constrained content areas
// Focuses on vertical scrolling with clean scrollbar design

import React, { forwardRef } from 'react';
import './scroll.css';

/**
 * Scrollable container component with custom styling
 * @param {object} props - Scroll props
 * @param {React.ReactNode} props.children - Content to scroll
 * @param {string} props.maxHeight - Maximum height (CSS value like '200px', '50vh')
 * @param {string} props.direction - Scroll direction ('vertical', 'horizontal', 'both')
 * @param {string} props.size - Scrollbar size (sm, md, lg)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {object} props.rest - Additional div attributes
 * @returns {React.ReactElement} Scroll component
 */
const Scroll = forwardRef(function Scroll({
  children,
  maxHeight = '200px',
  direction = 'vertical',
  size = 'md',
  className = '',
  style = {},
  ...rest
}, ref) {
  
  // Build CSS classes
  const scrollClasses = [
    'scroll-container',
    `scroll-${direction}`,
    `scroll-${size}`,
    className
  ].filter(Boolean).join(' ');

  // Combine styles with maxHeight
  const containerStyle = {
    maxHeight,
    ...style
  };

  return (
    <div 
      ref={ref}
      className={scrollClasses}
      style={containerStyle}
      {...rest}
    >
      <div className="scroll-content">
        {children}
      </div>
    </div>
  );
});

// Direction constants for easy imports
export const SCROLL_DIRECTIONS = {
  VERTICAL: 'vertical',
  HORIZONTAL: 'horizontal',
  BOTH: 'both'
};

// Size constants for easy imports
export const SCROLL_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};

export default Scroll;