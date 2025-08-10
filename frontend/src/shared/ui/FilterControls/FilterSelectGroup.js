// FilterSelectGroup Component - Dynamic filter dropdown generator
// Takes filter options object and creates formatted dropdown boxes for each filter
// Uses existing Select component with proper label formatting

import React from 'react';
import { Select, FormField } from '../Form/index.js';
import './FilterControls.css';

/**
 * Utility function to format field names into readable labels
 * Converts snake_case/camelCase to Title Case
 * @param {string} fieldName - Field name to format (e.g., 'prompt_name', 'generationType')
 * @returns {string} Formatted label (e.g., 'Prompt Name', 'Generation Type')
 */
function formatFieldLabel(fieldName) {
  return fieldName
    // Handle camelCase: insert space before uppercase letters
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    // Handle snake_case: replace underscores with spaces
    .replace(/_/g, ' ')
    // Capitalize first letter of each word
    .replace(/\b\w/g, letter => letter.toUpperCase());
}

/**
 * FilterSelectGroup Component - Creates multiple filter dropdowns from options object
 * @param {object} props - FilterSelectGroup props
 * @param {object} props.filterOptions - Object with filter field names as keys and option arrays as values
 * @param {object} props.values - Current filter values object (e.g., {generation_type: 'llm', priority: 5})
 * @param {Function} props.onChange - Called when any filter changes: (fieldName, value, allValues) => {}
 * @param {boolean} props.disabled - Disable all dropdowns
 * @param {object} props.errors - Errors object with field names as keys
 * @param {string} props.layout - Layout style: 'grid' | 'horizontal' | 'vertical' (default: 'grid')
 * @param {object} props.customLabels - Override labels for specific fields (e.g., {prompt_name: 'Custom Prompt'})
 * @param {boolean} props.showPlaceholders - Show "Select..." placeholders (default: true)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} FilterSelectGroup component
 */
function FilterSelectGroup({
  filterOptions = {},
  values = {},
  onChange = null,
  disabled = false,
  errors = {},
  layout = 'grid',
  customLabels = {},
  showPlaceholders = true,
  className = '',
  ...rest
}) {

  // Handle individual filter change
  const handleFilterChange = (fieldName) => (event) => {
    const newValue = event.target.value;
    
    // Create updated values object
    const updatedValues = {
      ...values,
      [fieldName]: newValue || undefined // Remove empty values
    };

    // Call onChange with field name, new value, and complete values object
    if (onChange) {
      onChange(fieldName, newValue, updatedValues);
    }
  };

  // Generate CSS classes
  const containerClasses = [
    'filter-select-group',
    `filter-select-group-${layout}`,
    disabled && 'filter-select-group-disabled',
    className
  ].filter(Boolean).join(' ');

  // Generate filter fields from options
  const filterFields = Object.entries(filterOptions).map(([fieldName, options]) => {
    // Determine label (custom or auto-formatted)
    const label = customLabels[fieldName] || formatFieldLabel(fieldName);
    
    // Handle different option formats
    let selectOptions = [];
    
    if (Array.isArray(options)) {
      // Simple array of values
      selectOptions = options.map(option => ({
        value: option,
        label: String(option)
      }));
    } else if (typeof options === 'object' && options !== null) {
      // Object with {value: label} pairs
      selectOptions = Object.entries(options).map(([value, label]) => ({
        value,
        label: String(label)
      }));
    }

    // Get current value for this field
    const currentValue = values[fieldName] || '';
    
    // Get error for this field
    const fieldError = errors[fieldName] || null;

    // Generate placeholder text
    const placeholder = showPlaceholders ? `Select ${label}...` : undefined;

    return (
      <div key={fieldName} className="filter-select-item">
        <FormField
          label={label}
          error={fieldError}
        >
          <Select
            value={currentValue}
            onChange={handleFilterChange(fieldName)}
            options={selectOptions}
            disabled={disabled}
            className="filter-select"
          />
        </FormField>
      </div>
    );
  });

  return (
    <div className={containerClasses} {...rest}>
      {filterFields}
    </div>
  );
}

export default FilterSelectGroup;