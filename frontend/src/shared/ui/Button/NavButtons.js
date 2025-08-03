// NavButtons Component - Reusable navigation button group
// Uses ButtonGroup and Button from shared UI for consistent styling
// Perfect for app navigation, tab switching, or any grouped button navigation

import React from 'react';
import { ButtonGroup, Button } from '../index.js';

/**
 * Navigation button group component
 * @param {object} props - NavButtons props
 * @param {Array} props.buttons - Array of button objects with {screen, label} 
 * @param {string} props.activeScreen - Currently active screen identifier
 * @param {Function} props.onScreenChange - Called when a button is clicked
 * @param {string} props.spacing - ButtonGroup spacing ('tight', 'normal', 'loose')
 * @param {string} props.alignment - ButtonGroup alignment ('start', 'center', 'end')
 * @param {string} props.size - Button size ('sm', 'md', 'lg')
 * @param {string} props.className - Additional CSS classes
 * @returns {React.ReactElement} NavButtons component
 */
function NavButtons({
  buttons = [],
  activeScreen = null,
  onScreenChange = null,
  spacing = 'tight',
  alignment = 'center', 
  size = 'sm',
  className = ''
}) {

  return (
    <ButtonGroup 
      spacing={spacing}
      alignment={alignment}
      className={`nav-buttons ${className}`}
    >
      {buttons.map((button) => (
        <Button
          key={button.screen}
          variant={activeScreen === button.screen ? 'secondary' : 'primary'}
          size={size}
          onClick={() => onScreenChange?.(button.screen)}
        >
          {button.label}
        </Button>
      ))}
    </ButtonGroup>
  );
}

export default NavButtons;