// Form Component - Simple form container with submission handling
// Handles form submission, loading states, and form-level errors
// Coordinates validation and provides consistent form behavior

import React from 'react';
import './form.css';

/**
 * Simple Form container component with submission handling
 * @param {object} props - Form props
 * @param {React.ReactNode} props.children - Form content (FormField components, etc.)
 * @param {Function} props.onSubmit - Form submission handler
 * @param {boolean} props.loading - Show loading state during submission
 * @param {boolean} props.disabled - Disable entire form
 * @param {string} props.error - Form-level error message
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML form attributes
 */
function Form({
  children,
  onSubmit = null,
  loading = false,
  disabled = false,
  error = null,
  className = '',
  ...rest
}) {
  
  const formClasses = [
    'form',
    loading && 'form-loading',
    disabled && 'form-disabled',
    error && 'form-with-error',
    className
  ].filter(Boolean).join(' ');

  // Handle form submission
  const handleSubmit = (event) => {
    event.preventDefault();
    
    if (loading || disabled) {
      return;
    }
    
    if (onSubmit) {
      onSubmit(event);
    }
  };

  return (
    <form
      className={formClasses}
      onSubmit={handleSubmit}
      {...rest}
    >
      {/* Form-level error message */}
      {error && (
        <div className="form-error-message">
          ❌ {error}
        </div>
      )}
      
      {/* Form content */}
      <div className="form-content">
        {children}
      </div>
      
      {/* Loading overlay (if needed) */}
      {loading && (
        <div className="form-loading-overlay">
          🔄 Processing...
        </div>
      )}
    </form>
  );
}

export default Form;