// Input Component - SIMPLIFIED
// Basic text input for future form needs
// Handles text, email, password, number types

import React from 'react';

/**
 * Simple Input component for text inputs
 * @param {object} props - Input props
 * @param {string} props.type - Input type (text, email, password, number)
 * @param {string} props.value - Current input value
 * @param {Function} props.onChange - Change handler  
 * @param {string} props.placeholder - Placeholder text
 * @param {boolean} props.disabled - Disable input
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML input attributes
 */
function Input({
  type = 'text',
  value = '',
  onChange = null,
  placeholder = '',
  disabled = false,
  className = '',
  ...rest
}) {
  
  const inputClasses = [
    'form-input',
    disabled && 'form-input-disabled',
    className
  ].filter(Boolean).join(' ');

  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      className={inputClasses}
      {...rest}
    />
  );
}

export default Input;