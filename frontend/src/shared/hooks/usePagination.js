// usePagination Hook - React state management for pagination
// Uses pagination utilities for calculations, provides React state and actions
// Handles all pagination state and provides convenient action functions

import { useState, useCallback, useMemo } from 'react';
import {
  calculateTotalPages,
  calculateOffset,
  hasNextPage,
  hasPrevPage,
  getNextPage,
  getPrevPage,
  createPaginationInfo,
  normalizePage
} from '../utils/pagination.js';

/**
 * Hook for pagination state management with utility-based calculations
 * @param {object} options - Pagination configuration
 * @param {number} options.limit - Items per page (default: 12)
 * @param {number} options.total - Total number of items (optional, for calculations)
 * @param {number} options.initialPage - Starting page (default: 1)
 * @returns {object} Pagination state and actions
 */
export function usePagination(options = {}) {
  const {
    limit = 12,
    total = null,
    initialPage = 1
  } = options;

  // Core pagination state
  const [currentPage, setCurrentPage] = useState(initialPage);

  // Calculated values using utilities (memoized for performance)
  const currentOffset = useMemo(() => {
    return calculateOffset(currentPage, limit);
  }, [currentPage, limit]);

  const totalPages = useMemo(() => {
    if (total === null || total === undefined) return null;
    return calculateTotalPages(total, limit);
  }, [total, limit]);

  const hasNext = useMemo(() => {
    if (totalPages === null) return null; // Unknown if no total provided
    return hasNextPage(currentPage, totalPages);
  }, [currentPage, totalPages]);

  const hasPrev = useMemo(() => {
    return hasPrevPage(currentPage);
  }, [currentPage]);

  // Complete pagination info object (when total is known)
  const paginationInfo = useMemo(() => {
    if (total === null || total === undefined) return null;
    return createPaginationInfo(currentPage, total, limit);
  }, [currentPage, total, limit]);

  /**
   * Navigate to specific page
   * Automatically normalizes page to valid range if total is known
   * @param {number} page - Target page (1-based)
   */
  const goToPage = useCallback((page) => {
    if (totalPages !== null) {
      // Normalize page to valid range when total is known
      const validPage = normalizePage(page, totalPages);
      setCurrentPage(validPage);
    } else {
      // When total unknown, just ensure page >= 1
      const safePage = Math.max(1, page);
      setCurrentPage(safePage);
    }
  }, [totalPages]);

  /**
   * Navigate to next page
   * Only advances if next page exists (when total is known) or unconditionally (when total unknown)
   */
  const nextPage = useCallback(() => {
    if (totalPages !== null) {
      // When total is known, check if next page exists
      const nextPageNum = getNextPage(currentPage, totalPages);
      if (nextPageNum !== null) {
        setCurrentPage(nextPageNum);
      }
    } else {
      // When total unknown, just increment (component should handle limits)
      setCurrentPage(prev => prev + 1);
    }
  }, [currentPage, totalPages]);

  /**
   * Navigate to previous page
   * Only goes back if previous page exists
   */
  const prevPage = useCallback(() => {
    const prevPageNum = getPrevPage(currentPage);
    if (prevPageNum !== null) {
      setCurrentPage(prevPageNum);
    }
  }, [currentPage]);

  /**
   * Navigate to first page
   */
  const firstPage = useCallback(() => {
    setCurrentPage(1);
  }, []);

  /**
   * Navigate to last page (only when total is known)
   */
  const lastPage = useCallback(() => {
    if (totalPages !== null && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [totalPages]);

  /**
   * Reset pagination to initial page
   */
  const reset = useCallback(() => {
    setCurrentPage(initialPage);
  }, [initialPage]);

  /**
   * Set new limit and adjust current page if necessary
   * Useful when user changes items per page
   * @param {number} newLimit - New items per page
   */
  const setLimit = useCallback((newLimit) => {
    if (total !== null) {
      // Calculate what the current page should be with new limit
      const currentOffset = calculateOffset(currentPage, limit);
      const newPage = Math.floor(currentOffset / newLimit) + 1;
      const newTotalPages = calculateTotalPages(total, newLimit);
      const validPage = normalizePage(newPage, newTotalPages);
      setCurrentPage(validPage);
    }
    // Note: Component should update the limit in its own state
  }, [currentPage, limit, total]);

  return {
    // Current state
    currentPage,
    currentOffset,
    limit,
    total,

    // Calculated values (null if total unknown)
    totalPages,
    hasNext,
    hasPrev,

    // Convenience flags
    isFirstPage: currentPage === 1,
    isLastPage: totalPages !== null ? currentPage === totalPages : false,
    canGoNext: hasNext !== false, // true if unknown or if next exists
    canGoPrev: hasPrev,

    // Complete pagination info (null if total unknown)
    paginationInfo,

    // Actions
    goToPage,
    nextPage,
    prevPage,
    firstPage,
    lastPage,
    reset,
    setLimit,

    // Utilities (re-exported for convenience)
    utils: {
      calculateTotalPages,
      calculateOffset,
      hasNextPage,
      hasPrevPage,
      createPaginationInfo,
      normalizePage
    }
  };
}

/**
 * Lightweight pagination hook for when you only need basic state
 * No calculations, just current page state and basic actions
 * @param {number} initialPage - Starting page (default: 1)
 * @returns {object} Basic pagination state
 */
export function useSimplePagination(initialPage = 1) {
  const [currentPage, setCurrentPage] = useState(initialPage);
  
  const goToPage = useCallback((page) => {
    setCurrentPage(Math.max(1, page));
  }, []);

  const nextPage = useCallback(() => {
    setCurrentPage(prev => prev + 1);
  }, []);

  const prevPage = useCallback(() => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  }, []);

  const reset = useCallback(() => {
    setCurrentPage(initialPage);
  }, [initialPage]);

  return {
    currentPage,
    currentOffset: calculateOffset(currentPage, 12), // Assumes default limit
    goToPage,
    nextPage,
    prevPage,
    reset
  };
}

// Usage Examples:
//
// Basic usage (when you know total):
// const pagination = usePagination({ 
//   limit: 12, 
//   total: 150 
// });
//
// Usage when total unknown (infinite scroll, etc.):
// const pagination = usePagination({ limit: 12 });
//
// Simple usage (minimal state):
// const pagination = useSimplePagination();
//
// In components:
// const { currentPage, currentOffset, hasNext, goToPage, nextPage } = pagination;
//
// For API calls:
// loadData({ limit: pagination.limit, offset: pagination.currentOffset });
//
// For pagination controls:
// <button onClick={() => pagination.prevPage()} disabled={!pagination.hasPrev}>
//   Previous
// </button>