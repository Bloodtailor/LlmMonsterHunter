// PlaceholderCard Components - Individual placeholder components for different contexts
// Uses theme.css card dimensions for consistent sizing with monster cards
// Each placeholder type is its own component function

import React from 'react';

// Base styles for all placeholders
const getPlaceholderBaseStyles = (size) => ({
  width: `var(--card-width-${size})`,
  height: `var(--card-height-${size})`,
  border: '2px dashed var(--background-light)',
  borderRadius: 'var(--radius-lg)',
  backgroundColor: 'var(--background-dark)',
});

/**
 * Empty Party Slot - Placeholder for adding monsters to party
 */
export function EmptyPartySlot({ children, size = 'md', className = '', style = {}, ...props }) {
  
  const combinedStyles = {
    ...getPlaceholderBaseStyles(size),
    ...style
  };

  const classes = [
    'placeholder-card',
    'empty-party-slot',
    `placeholder-card-${size}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div 
      className={classes}
      style={combinedStyles}
      {...props}
    >
      {children}
    </div>
  );
}

// Default export for backwards compatibility
export default EmptyPartySlot;

