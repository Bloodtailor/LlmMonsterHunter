// Full-Featured Pagination Component - SIMPLIFIED LAYOUTS
// Three clean layout options: default, simple, full
// Eliminates complex boolean props in favor of clear layout choices

import React from 'react';
import {
  Pagination as PaginationPrimitive,
  PaginationInfo,
  PageJumper,
  ItemsPerPageSelector
} from './index.js';

/**
 * Complete pagination component with clean layout options
 * @param {object} props - Pagination props
 * @param {object} props.pagination - Pagination object from usePagination hook
 * @param {string} props.itemName - Name of items being paginated (default: 'items')
 * @param {string} props.layout - Layout style ('default', 'simple', 'full') (default: 'default')
 * @param {Array} props.itemsPerPageOptions - Options for items per page (default: [5, 10, 25, 50]) - only used in 'full' layout
 * @param {number} props.currentLimit - Current items per page value - only used in 'full' layout
 * @param {Function} props.onLimitChange - Callback when items per page changes - only used in 'full' layout
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} Complete pagination component
 */
function Pagination({
  pagination,
  itemName = 'items',
  layout = 'default',
  itemsPerPageOptions = [5, 10, 25, 50],
  currentLimit = null,
  onLimitChange = null,
  className = '',
  ...rest
}) {
  
  // Don't render if no pagination data
  if (!pagination || !pagination.paginationInfo) {
    return null;
  }

  const fullPaginationClasses = [
    'full-pagination',
    `full-pagination-${layout}`,
    className
  ].filter(Boolean).join(' ');

  // Default Layout: Just the main pagination primitive
  if (layout === 'default') {
    return (
      <div className={fullPaginationClasses} {...rest}>
        <div className="full-pagination-default">
          <PaginationPrimitive
            pagination={pagination}
            showFirstLast={true}
            showPrevNext={true}
          />
        </div>
      </div>
    );
  }

  // Simple Layout: Info + Basic Pagination
  if (layout === 'simple') {
    return (
      <div className={fullPaginationClasses} {...rest}>
        <div className="full-pagination-simple">
          <div className="full-pagination-simple-info">
            <PaginationInfo pagination={pagination} itemName={itemName} />
          </div>
          <div className="full-pagination-simple-pagination">
            <PaginationPrimitive
              pagination={pagination}
              showFirstLast={false} // Simpler - no first/last buttons
              showPrevNext={true}
            />
          </div>
        </div>
      </div>
    );
  }

  // Full Layout: Items per page (left) + Pagination (center) + Jumper (right)
  if (layout === 'full') {
    return (
      <div className={fullPaginationClasses} {...rest}>
        <div className="full-pagination-full">
          
          <div className="full-pagination-full-left">
            {currentLimit && onLimitChange && (
              <ItemsPerPageSelector
                value={currentLimit}
                onChange={onLimitChange}
                options={itemsPerPageOptions}
                itemName={itemName}
              />
            )}
          </div>
          
          <div className="full-pagination-full-center">
            <PaginationPrimitive
              pagination={pagination}
              showFirstLast={true}
              showPrevNext={true}
            />
          </div>
          
          <div className="full-pagination-full-right">
            <PageJumper pagination={pagination} />
          </div>
          
        </div>
      </div>
    );
  }

  // Fallback to default layout
  return (
    <div className={fullPaginationClasses} {...rest}>
      <PaginationPrimitive pagination={pagination} />
    </div>
  );
}

// Layout constants for easy imports
export const PAGINATION_LAYOUTS = {
  DEFAULT: 'default',   // Just pagination primitive
  SIMPLE: 'simple',     // Info + basic pagination
  FULL: 'full'          // Items per page + pagination + jumper
};

export default Pagination;