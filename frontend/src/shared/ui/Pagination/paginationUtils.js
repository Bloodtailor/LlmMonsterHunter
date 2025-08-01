// Pagination Utilities - Pure calculation functions for pagination logic
// Reusable anywhere: React hooks, components, backend, tests, etc.
// No React dependencies - just math and logic

/**
 * Calculate total number of pages based on total items and items per page
 * @param {number} total - Total number of items
 * @param {number} limit - Items per page
 * @returns {number} Total pages (minimum 1)
 */
export function calculateTotalPages(total, limit) {
  if (!total || total <= 0) return 1;
  if (!limit || limit <= 0) return 1;
  return Math.ceil(total / limit);
}

/**
 * Calculate offset for API calls based on page and limit
 * @param {number} page - Current page (1-based)
 * @param {number} limit - Items per page
 * @returns {number} Offset for API calls (0-based)
 */
export function calculateOffset(page, limit) {
  if (!page || page < 1) return 0;
  if (!limit || limit <= 0) return 0;
  return (page - 1) * limit;
}

/**
 * Check if there's a next page available
 * @param {number} currentPage - Current page (1-based)
 * @param {number} totalPages - Total number of pages
 * @returns {boolean} True if next page exists
 */
export function hasNextPage(currentPage, totalPages) {
  if (!currentPage || !totalPages) return false;
  return currentPage < totalPages;
}

/**
 * Check if there's a previous page available
 * @param {number} currentPage - Current page (1-based)
 * @returns {boolean} True if previous page exists
 */
export function hasPrevPage(currentPage) {
  if (!currentPage) return false;
  return currentPage > 1;
}

/**
 * Validate if a page number is within valid range
 * @param {number} page - Page to validate (1-based)
 * @param {number} totalPages - Total number of pages
 * @returns {boolean} True if page is valid
 */
export function isValidPage(page, totalPages) {
  if (!page || !totalPages) return false;
  return page >= 1 && page <= totalPages;
}

/**
 * Get next page number, or null if no next page
 * @param {number} currentPage - Current page (1-based)
 * @param {number} totalPages - Total number of pages
 * @returns {number|null} Next page number or null
 */
export function getNextPage(currentPage, totalPages) {
  if (!hasNextPage(currentPage, totalPages)) return null;
  return currentPage + 1;
}

/**
 * Get previous page number, or null if no previous page
 * @param {number} currentPage - Current page (1-based)
 * @returns {number|null} Previous page number or null
 */
export function getPrevPage(currentPage) {
  if (!hasPrevPage(currentPage)) return null;
  return currentPage - 1;
}

/**
 * Generate array of page numbers for pagination controls
 * Useful for creating "1 2 3 ... 8 9 10" style pagination
 * @param {number} currentPage - Current page (1-based)
 * @param {number} totalPages - Total number of pages
 * @param {number} rangeSize - Number of pages to show around current (default: 5)
 * @returns {Array} Array of page numbers and ellipsis indicators
 */
export function getPageRange(currentPage, totalPages, rangeSize = 5) {
  if (!currentPage || !totalPages || totalPages <= 1) {
    return [1];
  }

  // If total pages fit in range, show all
  if (totalPages <= rangeSize) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const range = [];
  const halfRange = Math.floor(rangeSize / 2);

  // Always show first page
  range.push(1);

  // Calculate start and end of middle range
  let start = Math.max(2, currentPage - halfRange);
  let end = Math.min(totalPages - 1, currentPage + halfRange);

  // Adjust if we're near the beginning
  if (currentPage - halfRange <= 1) {
    end = Math.min(totalPages - 1, rangeSize - 1);
  }

  // Adjust if we're near the end
  if (currentPage + halfRange >= totalPages) {
    start = Math.max(2, totalPages - rangeSize + 2);
  }

  // Add ellipsis before middle range if needed
  if (start > 2) {
    range.push('...');
  }

  // Add middle range
  for (let i = start; i <= end; i++) {
    range.push(i);
  }

  // Add ellipsis after middle range if needed
  if (end < totalPages - 1) {
    range.push('...');
  }

  // Always show last page (if not already included)
  if (totalPages > 1) {
    range.push(totalPages);
  }

  return range;
}

/**
 * Create pagination info object with all calculated values
 * Useful for components that need multiple pagination properties
 * @param {number} currentPage - Current page (1-based)
 * @param {number} total - Total number of items
 * @param {number} limit - Items per page
 * @returns {object} Complete pagination info
 */
export function createPaginationInfo(currentPage, total, limit) {
  const totalPages = calculateTotalPages(total, limit);
  const offset = calculateOffset(currentPage, limit);
  
  return {
    currentPage,
    totalPages,
    total,
    limit,
    offset,
    hasNext: hasNextPage(currentPage, totalPages),
    hasPrev: hasPrevPage(currentPage),
    nextPage: getNextPage(currentPage, totalPages),
    prevPage: getPrevPage(currentPage),
    isFirstPage: currentPage === 1,
    isLastPage: currentPage === totalPages,
    pageRange: getPageRange(currentPage, totalPages),
    
    // Useful for display
    startItem: total > 0 ? offset + 1 : 0,
    endItem: Math.min(offset + limit, total),
    
    // Validation
    isValid: isValidPage(currentPage, totalPages)
  };
}

/**
 * Safe page number normalization
 * Ensures page is within valid bounds
 * @param {number} page - Page to normalize
 * @param {number} totalPages - Total number of pages
 * @returns {number} Valid page number (1-based)
 */
export function normalizePage(page, totalPages) {
  if (!page || page < 1) return 1;
  if (!totalPages || totalPages < 1) return 1;
  if (page > totalPages) return totalPages;
  return page;
}

// Export all functions as a single object for convenience
export const paginationUtils = {
  calculateTotalPages,
  calculateOffset,
  hasNextPage,
  hasPrevPage,
  isValidPage,
  getNextPage,
  getPrevPage,
  getPageRange,
  createPaginationInfo,
  normalizePage
};