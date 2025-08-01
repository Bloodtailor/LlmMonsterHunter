// PaginationInfo Component - Displays "Showing X-Y of Z items" information
// Simple text display of current pagination status
// Uses pagination info object for calculations

import React from 'react';
import './pagination.css';

/**
 * Pagination information display component
 * @param {object} props - PaginationInfo props
 * @param {object} props.pagination - Pagination object from usePagination hook
 * @param {string} props.itemName - Name of items being paginated (default: 'items')
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} PaginationInfo component
 */
function PaginationInfo({
  pagination,
  itemName = 'items',
  className = '',
  ...rest
}) {
  
  // Don't render if no pagination data
  if (!pagination || !pagination.paginationInfo) {
    return null;
  }

  const { paginationInfo } = pagination;
  const { startItem, endItem, total } = paginationInfo;

  const infoClasses = [
    'pagination-info',
    className
  ].filter(Boolean).join(' ');

  // Handle different scenarios
  if (total === 0) {
    return (
      <div className={infoClasses} {...rest}>
        <span className="pagination-info-text">
          No {itemName} found
        </span>
      </div>
    );
  }

  if (total === 1) {
    return (
      <div className={infoClasses} {...rest}>
        <span className="pagination-info-text">
          Showing 1 {itemName === 'items' ? 'item' : itemName}
        </span>
      </div>
    );
  }

  return (
    <div className={infoClasses} {...rest}>
      <span className="pagination-info-text">
        Showing <strong>{startItem}</strong>-<strong>{endItem}</strong> of <strong>{total}</strong> {itemName}
      </span>
    </div>
  );
}

export default PaginationInfo;