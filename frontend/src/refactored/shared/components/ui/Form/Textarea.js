// Textarea Component - Multi-line text input with error handling
// Essential for descriptions, backstories, and longer text content
// Built with same patterns as Input for consistency

import React from 'react';

/**
 * Simple Textarea component for multi-line text input
 * @param {object} props - Textarea props
 * @param {string} props.value - Current textarea value
 * @param {Function} props.onChange - Change handler  
 * @param {string} props.placeholder - Placeholder text
 * @param {boolean} props.disabled - Disable textarea
 * @param {string} props.error - Error message to display
 * @param {number} props.rows - Number of visible text lines (default: 4)
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML textarea attributes
 */
function Textarea({
  value = '',
  onChange = null,
  placeholder = '',
  disabled = false,
  error = null,
  rows = 4,
  className = '',
  ...rest
}) {
  
  const textareaClasses = [
    'form-textarea',
    disabled && 'form-textarea-disabled',
    error && 'form-textarea-error',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-textarea-container">
      <textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        rows={rows}
        className={textareaClasses}
        {...rest}
      />
      
      {error && (
        <div className="form-textarea-error-message">
          {error}
        </div>
      )}
    </div>
  );
}

export default Textarea;