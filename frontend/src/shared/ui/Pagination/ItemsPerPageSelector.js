// ItemsPerPageSelector Component - "Items per page: [select]" dropdown
// Allows user to change how many items are displayed per page
// Uses existing Select component

import React from 'react';
import { Select } from '../Form/index.js';
import './pagination.css';

/**
 * Items per page selector component
 * @param {object} props - ItemsPerPageSelector props
 * @param {number} props.value - Current items per page value
 * @param {Function} props.onChange - Change handler function
 * @param {Array} props.options - Available options (default: [5, 10, 25, 50])
 * @param {string} props.itemName - Name of items (default: 'items')
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} ItemsPerPageSelector component
 */
function ItemsPerPageSelector({
  value,
  onChange,
  options = [5, 10, 25, 50],
  itemName = 'items',
  className = '',
  ...rest
}) {
  
  const selectorClasses = [
    'items-per-page-selector',
    className
  ].filter(Boolean).join(' ');

  // Format options for Select component
  const selectOptions = options.map(option => ({
    value: option,
    label: `${option} ${itemName} per page`
  }));

  const handleSelectChange = (event) => {
    const newValue = parseInt(event.target.value);
    if (onChange) {
      onChange(newValue);
    }
  };

  return (
    <div className={selectorClasses} {...rest}>
      <div className="items-per-page-controls">
        <span className="items-per-page-label">Show:</span>
        
        <Select
          value={value}
          onChange={handleSelectChange}
          options={selectOptions}
          className="items-per-page-select"
        />
      </div>
    </div>
  );
}

export default ItemsPerPageSelector;