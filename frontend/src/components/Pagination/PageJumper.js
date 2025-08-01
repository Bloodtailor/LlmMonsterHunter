// PageJumper Component - "Go to page: [input] [Go]" functionality
// Allows user to type page number and jump directly to it
// Uses existing Input and Button components

import React, { useState } from 'react';
import { Input } from '../Form/index.js';
import { Button } from '../Button/index.js';

/**
 * Page jumper component for direct page navigation
 * @param {object} props - PageJumper props
 * @param {object} props.pagination - Pagination object from usePagination hook
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} PageJumper component
 */
function PageJumper({
  pagination,
  className = '',
  ...rest
}) {
  const [inputValue, setInputValue] = useState('');

  // Don't render if no pagination data
  if (!pagination || !pagination.totalPages) {
    return null;
  }

  const { totalPages } = pagination;

  const jumperClasses = [
    'page-jumper',
    className
  ].filter(Boolean).join(' ');

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleJump = () => {
    const pageNumber = parseInt(inputValue);
    
    // Basic validation (user said assume valid input)
    if (pageNumber && pageNumber >= 1 && pageNumber <= totalPages) {
      pagination.goToPage(pageNumber);
      setInputValue(''); // Clear input after successful jump
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleJump();
    }
  };

  return (
    <div className={jumperClasses} {...rest}>
      <div className="page-jumper-controls">
        <span className="page-jumper-label">Go to page:</span>
        
        <Input
          type="number"
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="1"
          min="1"
          max={totalPages}
          className="page-jumper-input"
        />
        
        <Button
          variant="primary"
          size="sm"
          onClick={handleJump}
          disabled={!inputValue}
          className="page-jumper-button"
        >
          Go
        </Button>
      </div>
      
      <span className="page-jumper-info">
        of {totalPages}
      </span>
    </div>
  );
}

export default PageJumper;