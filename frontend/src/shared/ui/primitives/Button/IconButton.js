// IconButton Component - Specialized button for icon-only interactions
// Perfect for compact UI elements like party toggles, expand buttons, close buttons
// Built on top of the main Button component with icon-specific optimizations

import React from 'react';
import Button from './Button.js';

/**
 * Icon-only button component with optimized styling and behavior
 * @param {object} props - IconButton props
 * @param {string} props.icon - Icon to display (emoji or icon class) - REQUIRED
 * @param {string} props.variant - Button style variant (default: 'secondary')
 * @param {string} props.size - Button size (default: 'md')
 * @param {boolean} props.loading - Show loading state
 * @param {boolean} props.disabled - Disable button
 * @param {Function} props.onClick - Click handler
 * @param {string} props.ariaLabel - Accessibility label - REQUIRED for icon-only
 * @param {string} props.title - Tooltip text (will also be used as ariaLabel if not provided)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional props passed to Button
 * @returns {React.ReactElement} IconButton component
 */
function IconButton({
  icon,
  variant = 'secondary',
  size = 'md',
  loading = false,
  disabled = false,
  onClick = null,
  ariaLabel = null,
  title = null,
  className = '',
  ...rest
}) {
  
  // Validation
  if (!icon) {
    console.error('IconButton: icon prop is required');
    return null;
  }

  // Use title as ariaLabel fallback for accessibility
  const accessibilityLabel = ariaLabel || title || 'Icon button';

  // Add icon-specific CSS classes
  const iconButtonClasses = [
    'icon-button', // Specific icon button styling
    className
  ].filter(Boolean).join(' ');

  return (
    <Button
      variant={variant}
      size={size}
      loading={loading}
      disabled={disabled}
      onClick={onClick}
      icon={icon}
      ariaLabel={accessibilityLabel}
      title={title}
      className={iconButtonClasses}
      {...rest}
    />
  );
}

export default IconButton;