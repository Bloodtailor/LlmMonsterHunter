// Pagination Component - FIXED VERSION
// Fixed key conflicts, spacing, and rendering issues
// Uses pageRange for smart page number display (1 2 3 ... 8 9 10)

import React from 'react';
import { Button, IconButton } from '../Button/index.js';

/**
 * Main pagination component with numbered pages and navigation
 * @param {object} props - Pagination props
 * @param {object} props.pagination - Pagination object from usePagination hook
 * @param {boolean} props.showFirstLast - Show first/last buttons (default: true)
 * @param {boolean} props.showPrevNext - Show prev/next buttons (default: true)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} Pagination component
 */
function Pagination({
  pagination,
  showFirstLast = true,
  showPrevNext = true,
  className = '',
  ...rest
}) {
  
  // Don't render if no pagination data
  if (!pagination || !pagination.paginationInfo) {
    return null;
  }

  const {
    currentPage,
    totalPages,
    hasNext,
    hasPrev,
    isFirstPage,
    isLastPage,
    paginationInfo
  } = pagination;

  const paginationClasses = [
    'pagination',
    className
  ].filter(Boolean).join(' ');

  // Render page number or ellipsis - FIXED VERSION
  const renderPageItem = (page, index) => {
    // Use index as key to avoid conflicts between numbers and "..."
    const itemKey = `page-item-${index}`;
    
    if (page === '...') {
      return (
        <span key={itemKey} className="pagination-ellipsis" style={{ margin: '0 4px' }}>
          ...
        </span>
      );
    }

    const isCurrentPage = page === currentPage;
    
    return (
      <Button
        key={itemKey}
        variant={isCurrentPage ? 'ghost' : 'primary'}
        size="sm"
        onClick={() => pagination.goToPage(page)}
        disabled={isCurrentPage}
        className="pagination-page-button"
        style={{ margin: '0 2px' }}
      >
        {page}
      </Button>
    );
  };

  return (
    <div className={paginationClasses} style={{ display: 'flex', alignItems: 'center', gap: '8px' }} {...rest}>
      <div className="pagination-controls" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        
        {/* First Page Button */}
        {showFirstLast && (
          <IconButton
            icon="⏮️"
            variant="primary"
            size="sm"
            onClick={pagination.firstPage}
            disabled={isFirstPage}
            ariaLabel="Go to first page"
            className="pagination-first"
          />
        )}

        {/* Previous Page Button */}
        {showPrevNext && (
          <IconButton
            icon="⬅️"
            variant="primary"
            size="sm"
            onClick={pagination.prevPage}
            disabled={!hasPrev}
            ariaLabel="Go to previous page"
            className="pagination-prev"
          />
        )}

        {/* Page Numbers - FIXED VERSION */}
        <div className="pagination-pages" style={{ display: 'flex', alignItems: 'center' }}>
          {paginationInfo.pageRange.map(renderPageItem)}
        </div>

        {/* Next Page Button */}
        {showPrevNext && (
          <IconButton
            icon="➡️"
            variant="primary"
            size="sm"
            onClick={pagination.nextPage}
            disabled={!hasNext}
            ariaLabel="Go to next page"
            className="pagination-next"
          />
        )}

        {/* Last Page Button */}
        {showFirstLast && (
          <IconButton
            icon="⏭️"
            variant="primary"
            size="sm"
            onClick={pagination.lastPage}
            disabled={isLastPage}
            ariaLabel="Go to last page"
            className="pagination-last"
          />
        )}

      </div>
    </div>
  );
}

export default Pagination;