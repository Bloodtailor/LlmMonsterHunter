// Select Component - SIMPLIFIED
// Direct replacement for scattered select elements throughout codebase
// Supports both simple arrays and object options with icons

import React from 'react';

/**
 * Simple Select component for dropdowns
 * @param {object} props - Select props
 * @param {Array} props.options - Options (strings or {value, label, icon?} objects)
 * @param {string} props.value - Current selected value
 * @param {Function} props.onChange - Change handler
 * @param {string} props.placeholder - Placeholder text (optional)
 * @param {boolean} props.disabled - Disable select
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML select attributes
 */
function Select({
  options = [],
  value = '',
  onChange = null,
  placeholder = null,
  disabled = false,
  className = '',
  ...rest
}) {
  
  // Normalize options to {value, label, icon} format
  const normalizedOptions = options.map((option, index) => {
    if (typeof option === 'string') {
      return { value: option, label: option };
    }
    return {
      value: option.value,
      label: option.label || option.value,
      icon: option.icon || null
    };
  });

  const selectClasses = [
    'form-select',
    disabled && 'form-select-disabled',
    className
  ].filter(Boolean).join(' ');

  return (
    <select
      value={value}
      onChange={onChange}
      disabled={disabled}
      className={selectClasses}
      {...rest}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      
      {normalizedOptions.map((option, index) => {
        const displayLabel = option.icon ? `${option.icon} ${option.label}` : option.label;
        return (
          <option key={index} value={option.value}>
            {displayLabel}
          </option>
        );
      })}
    </select>
  );
}

export default Select;