// SearchInput Component - SIMPLIFIED
// Input with search icon and clear button
// Perfect for filtering monsters, logs, etc.

import React from 'react';
import Input from './Input.js';

/**
 * Simple SearchInput component with icon, clear button, and error handling
 * @param {object} props - SearchInput props
 * @param {string} props.value - Current search value
 * @param {Function} props.onChange - Change handler
 * @param {string} props.placeholder - Placeholder text (default: "Search...")
 * @param {Function} props.onClear - Clear button handler (optional)
 * @param {boolean} props.disabled - Disable input
 * @param {string} props.error - Error message to display
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional props
 */
function SearchInput({
  value = '',
  onChange = null,
  placeholder = 'Search...',
  onClear = null,
  disabled = false,
  error = null,
  className = '',
  ...rest
}) {
  
  const handleClear = () => {
    const syntheticEvent = {
      target: { value: '' },
      type: 'change'
    };
    
    if (onChange) {
      onChange(syntheticEvent);
    }
    
    if (onClear) {
      onClear();
    }
  };

  const searchClasses = [
    'form-search-input',
    value && 'form-search-input-with-value',
    error && 'form-search-input-error',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-search-input-container">
      <div className={searchClasses}>
        <div className="form-search-icon">🔍</div>
        
        <Input
          type="search"
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          className="form-search-input-field"
          {...rest}
        />
        
        {value && !disabled && (
          <button
            type="button"
            className="form-search-clear"
            onClick={handleClear}
          >
            ✕
          </button>
        )}
      </div>
      
      {error && (
        <div className="form-search-input-error-message">
          {error}
        </div>
      )}
    </div>
  );
}

export default SearchInput;