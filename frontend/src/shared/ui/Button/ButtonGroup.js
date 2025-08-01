// ButtonGroup Component - Container for multiple related buttons
// Perfect for pagination controls, toolbar actions, and grouped interactions
// Provides consistent spacing and visual grouping

import React from 'react';
import './button.css';

/**
 * Container component for grouping multiple buttons
 * @param {object} props - ButtonGroup props
 * @param {React.ReactNode} props.children - Button components to group
 * @param {string} props.orientation - Layout direction ('horizontal' or 'vertical')
 * @param {string} props.spacing - Space between buttons ('tight', 'normal', 'loose')
 * @param {string} props.alignment - Button alignment ('start', 'center', 'end', 'stretch')
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} ButtonGroup component
 */
function ButtonGroup({
  children,
  orientation = 'horizontal',
  spacing = 'normal',
  alignment = 'start',
  className = '',
  style = {},
  ...rest
}) {
  
  // Build CSS classes based on props
  const groupClasses = [
    'button-group', // Base button group class
    `button-group-${orientation}`, // Orientation styling
    `button-group-spacing-${spacing}`, // Spacing styling
    `button-group-align-${alignment}`, // Alignment styling
    className // Additional classes
  ].filter(Boolean).join(' ');

  return (
    <div
      className={groupClasses}
      style={style}
      role="group"
      {...rest}
    >
      {children}
    </div>
  );
}

// Orientation constants for easy imports
export const BUTTON_GROUP_ORIENTATIONS = {
  HORIZONTAL: 'horizontal',
  VERTICAL: 'vertical'
};

// Spacing constants for easy imports
export const BUTTON_GROUP_SPACING = {
  TIGHT: 'tight',
  NORMAL: 'normal',
  LOOSE: 'loose'
};

// Alignment constants for easy imports
export const BUTTON_GROUP_ALIGNMENT = {
  START: 'start',
  CENTER: 'center', 
  END: 'end',
  STRETCH: 'stretch'
};

export default ButtonGroup;