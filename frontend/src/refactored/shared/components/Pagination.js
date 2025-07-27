// Full-Featured Pagination Component - Combines all pagination primitives
// Provides a complete pagination experience with sensible defaults
// Perfect for most use cases - just pass pagination object and optional configs

import React from 'react';
import {
  Pagination as PaginationPrimitive,
  PaginationInfo,
  PageJumper,
  ItemsPerPageSelector
} from '../ui/Pagination/index.js';

/**
 * Complete pagination component with all features
 * @param {object} props - Pagination props
 * @param {object} props.pagination - Pagination object from usePagination hook
 * @param {string} props.itemName - Name of items being paginated (default: 'items')
 * @param {boolean} props.showInfo - Show pagination info (default: true)
 * @param {boolean} props.showJumper - Show page jumper (default: true)
 * @param {boolean} props.showItemsPerPage - Show items per page selector (default: false)
 * @param {Array} props.itemsPerPageOptions - Options for items per page (default: [5, 10, 25, 50])
 * @param {number} props.currentLimit - Current items per page value (required if showItemsPerPage is true)
 * @param {Function} props.onLimitChange - Callback when items per page changes (required if showItemsPerPage is true)
 * @param {boolean} props.showFirstLast - Show first/last buttons on pagination (default: true)
 * @param {string} props.layout - Layout style ('default', 'compact', 'spread') (default: 'default')
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} Complete pagination component
 */
function Pagination({
  pagination,
  itemName = 'items',
  showInfo = true,
  showJumper = true,
  showItemsPerPage = false,
  itemsPerPageOptions = [5, 10, 25, 50],
  currentLimit = null,
  onLimitChange = null,
  showFirstLast = true,
  layout = 'default',
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

  // Default Layout: Info at top, pagination in middle, jumper at bottom
  if (layout === 'default') {
    return (
      <div className={fullPaginationClasses} {...rest}>
        
        {/* Top Row: Info and Items Per Page */}
        {(showInfo || showItemsPerPage) && (
          <div className="full-pagination-top">
            {showInfo && (
              <div className="full-pagination-info">
                <PaginationInfo pagination={pagination} itemName={itemName} />
              </div>
            )}
            
            {showItemsPerPage && currentLimit && onLimitChange && (
              <div className="full-pagination-items-per-page">
                <ItemsPerPageSelector
                  value={currentLimit}
                  onChange={onLimitChange}
                  options={itemsPerPageOptions}
                  itemName={itemName}
                />
              </div>
            )}
          </div>
        )}

        {/* Middle Row: Main Pagination */}
        <div className="full-pagination-main">
          <PaginationPrimitive
            pagination={pagination}
            showFirstLast={showFirstLast}
            showPrevNext={true}
          />
        </div>

        {/* Bottom Row: Page Jumper */}
        {showJumper && (
          <div className="full-pagination-bottom">
            <PageJumper pagination={pagination} />
          </div>
        )}

      </div>
    );
  }

  // Compact Layout: Everything in one row
  if (layout === 'compact') {
    return (
      <div className={fullPaginationClasses} {...rest}>
        <div className="full-pagination-compact-row">
          
          {showInfo && (
            <div className="full-pagination-compact-info">
              <PaginationInfo pagination={pagination} itemName={itemName} />
            </div>
          )}
          
          <div className="full-pagination-compact-main">
            <PaginationPrimitive
              pagination={pagination}
              showFirstLast={showFirstLast}
              showPrevNext={true}
            />
          </div>
          
          {showJumper && (
            <div className="full-pagination-compact-jumper">
              <PageJumper pagination={pagination} />
            </div>
          )}
          
        </div>
        
        {/* Items per page on separate row even in compact mode */}
        {showItemsPerPage && currentLimit && onLimitChange && (
          <div className="full-pagination-compact-items">
            <ItemsPerPageSelector
              value={currentLimit}
              onChange={onLimitChange}
              options={itemsPerPageOptions}
              itemName={itemName}
            />
          </div>
        )}
        
      </div>
    );
  }

  // Spread Layout: Info left, pagination center, jumper right
  if (layout === 'spread') {
    return (
      <div className={fullPaginationClasses} {...rest}>
        
        {/* Main spread row */}
        <div className="full-pagination-spread-row">
          
          <div className="full-pagination-spread-left">
            {showInfo && (
              <PaginationInfo pagination={pagination} itemName={itemName} />
            )}
          </div>
          
          <div className="full-pagination-spread-center">
            <PaginationPrimitive
              pagination={pagination}
              showFirstLast={showFirstLast}
              showPrevNext={true}
            />
          </div>
          
          <div className="full-pagination-spread-right">
            {showJumper && (
              <PageJumper pagination={pagination} />
            )}
          </div>
          
        </div>
        
        {/* Items per page below in spread mode */}
        {showItemsPerPage && currentLimit && onLimitChange && (
          <div className="full-pagination-spread-items">
            <ItemsPerPageSelector
              value={currentLimit}
              onChange={onLimitChange}
              options={itemsPerPageOptions}
              itemName={itemName}
            />
          </div>
        )}
        
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
  DEFAULT: 'default',
  COMPACT: 'compact',
  SPREAD: 'spread'
};

export default Pagination;