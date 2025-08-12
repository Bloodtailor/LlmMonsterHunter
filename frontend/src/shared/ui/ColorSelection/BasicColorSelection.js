// BasicColorSelection Component - Simple color picker dropdown
// Uses the dynamic color system to show all available colors
// Perfect for monster color selection, theme picking, etc.

import React, { useMemo, useState } from 'react';
import Select from '../Form/Select.js';
import { getAllColors } from '../../styles/color.js';
import './colorSelection.css';

/**
 * Basic color selection dropdown component
 * @param {object} props - BasicColorSelection props
 * @param {string} props.value - Currently selected color name (e.g., 'red-intense')
 * @param {Function} props.onChange - Called when color selection changes
 * @param {string} props.placeholder - Placeholder text (default: 'Select a color')
 * @param {boolean} props.disabled - Disable the selection
 * @param {string} props.error - Error message to display
 * @param {boolean} props.showHex - Show hex values in labels (default: false)
 * @param {boolean} props.showPreview - Show color preview box (default: true)
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional props passed to Select
 * @returns {React.ReactElement} BasicColorSelection component
 */
function BasicColorSelection({
  value = null, // Changed from '' to null
  onChange = null,
  placeholder = 'Select a color',
  disabled = false,
  error = null,
  showHex = false,
  showPreview = true,
  className = '',
  ...rest
}) {
  
  // Internal state for uncontrolled usage
  const [internalValue, setInternalValue] = useState('');
  
  // Use controlled value if provided, otherwise use internal state
  const currentValue = value !== null ? value : internalValue;
  
  // Generate color options from CSS
  const colorOptions = useMemo(() => {
    const colors = getAllColors();
    
    return colors.map(color => ({
      value: color.name,
      label: showHex ? `${color.displayName} (${color.hex})` : color.displayName
    }));
  }, [showHex]);

  // Get the selected color info for preview
  const selectedColor = useMemo(() => {
    if (!currentValue) return null;
    return getAllColors().find(color => color.name === currentValue);
  }, [currentValue]);

  // Handle selection change
  const handleChange = (event) => {
    const selectedColorName = event.target.value;
    const selectedColorObj = getAllColors().find(color => color.name === selectedColorName);
    
    // Update internal state if uncontrolled
    if (value === null) {
      setInternalValue(selectedColorName);
    }
    
    // Call onChange if provided
    if (onChange) {
      onChange(event, selectedColorObj);
    }
  };

  const colorSelectionClasses = [
    'basic-color-selection',
    showPreview && 'basic-color-selection-with-preview',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={colorSelectionClasses}>
      <div className="basic-color-selection-container">
        <Select
          options={colorOptions}
          value={currentValue}
          onChange={handleChange}
          placeholder={placeholder}
          disabled={disabled}
          error={error}
          className="basic-color-selection-select"
          {...rest}
        />
        
        {/* Color preview box */}
        {showPreview && (
          <div className="basic-color-preview">
            {selectedColor ? (
              <div 
                className="color-preview-box"
                style={{ backgroundColor: selectedColor.hex }}
                title={`${selectedColor.displayName} (${selectedColor.hex})`}
              />
            ) : (
              <div className="color-preview-box color-preview-empty" title="No color selected" />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default BasicColorSelection;