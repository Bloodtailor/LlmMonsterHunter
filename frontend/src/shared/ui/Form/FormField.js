// FormField Component - SIMPLIFIED
// Wrapper for label + input patterns scattered throughout codebase
// Handles the common case: label above input

import React, { cloneElement, isValidElement } from 'react';
import './form.css';

/**
 * Simple FormField wrapper for label + input combinations with error handling
 * @param {object} props - FormField props
 * @param {React.ReactElement} props.children - Input component (Input, Select, SearchInput)
 * @param {string} props.label - Field label text
 * @param {string} props.error - Error message to display
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML div attributes
 */
function FormField({
  children,
  label = null,
  error = null,
  className = '',
  ...rest
}) {
  
  // Generate unique ID for accessibility
  const fieldId = `field-${Math.random().toString(36).substr(2, 9)}`;

  // Add ID and error to child component
  const enhancedChild = isValidElement(children) 
    ? cloneElement(children, {
        id: fieldId,
        error: error || children.props.error, // Allow error on child or FormField
        ...children.props
      })
    : children;

  const fieldClasses = [
    'form-field',
    error && 'form-field-with-error',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={fieldClasses} {...rest}>
      {label && (
        <label htmlFor={fieldId} className="form-field-label">
          {label}
        </label>
      )}
      {enhancedChild}
    </div>
  );
}

export default FormField;