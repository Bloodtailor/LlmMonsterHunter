// useExpandableRows Hook - Manages expansion state for expandable table rows
// Provides clean API for expanding/collapsing rows with optional multi-row support
// Follows the hook pattern established in the codebase (like useMonsterCardViewer)

import { useState, useCallback, useMemo } from 'react';

/**
 * Custom hook for managing expandable table row state
 * Provides expansion state management and control functions
 * 
 * @param {object} options - Hook configuration options
 * @param {boolean} options.allowMultiple - Allow multiple rows expanded simultaneously (default: true)
 * @param {Array} options.defaultExpanded - Initially expanded row IDs (default: [])
 * @param {Function} options.onExpand - Callback when row expands: (rowId) => void
 * @param {Function} options.onCollapse - Callback when row collapses: (rowId) => void
 * @returns {object} Hook result with expansion state and control functions
 */
export function useExpandableRows({
  allowMultiple = true,
  defaultExpanded = [],
  onExpand = null,
  onCollapse = null
} = {}) {
  
  // Internal state: Set of expanded row IDs for efficient lookups
  const [expandedRows, setExpandedRows] = useState(() => new Set(defaultExpanded));

  /**
   * Toggle expansion state of a specific row
   * @param {string|number} rowId - Unique identifier for the row
   */
  const toggleRow = useCallback((rowId) => {
    setExpandedRows(prev => {
      const newExpanded = new Set(prev);
      
      if (newExpanded.has(rowId)) {
        // Collapse this row
        newExpanded.delete(rowId);
        onCollapse?.(rowId);
      } else {
        // Expand this row
        if (!allowMultiple) {
          // Single-row mode: collapse all others first
          newExpanded.clear();
        }
        newExpanded.add(rowId);
        onExpand?.(rowId);
      }
      
      return newExpanded;
    });
  }, [allowMultiple, onExpand, onCollapse]);

  /**
   * Expand a specific row (no-op if already expanded)
   * @param {string|number} rowId - Unique identifier for the row
   */
  const expandRow = useCallback((rowId) => {
    setExpandedRows(prev => {
      if (prev.has(rowId)) {
        return prev; // Already expanded, no change
      }
      
      const newExpanded = new Set(prev);
      
      if (!allowMultiple) {
        // Single-row mode: collapse all others first
        newExpanded.clear();
      }
      
      newExpanded.add(rowId);
      onExpand?.(rowId);
      return newExpanded;
    });
  }, [allowMultiple, onExpand]);

  /**
   * Collapse a specific row (no-op if already collapsed)
   * @param {string|number} rowId - Unique identifier for the row
   */
  const collapseRow = useCallback((rowId) => {
    setExpandedRows(prev => {
      if (!prev.has(rowId)) {
        return prev; // Already collapsed, no change
      }
      
      const newExpanded = new Set(prev);
      newExpanded.delete(rowId);
      onCollapse?.(rowId);
      return newExpanded;
    });
  }, [onCollapse]);

  /**
   * Collapse all expanded rows
   */
  const collapseAll = useCallback(() => {
    setExpandedRows(prev => {
      if (prev.size === 0) {
        return prev; // Nothing to collapse
      }
      
      // Call onCollapse for each currently expanded row
      if (onCollapse) {
        prev.forEach(rowId => onCollapse(rowId));
      }
      
      return new Set(); // Empty set = no expanded rows
    });
  }, [onCollapse]);

  /**
   * Expand all rows from provided data
   * @param {Array} data - Array of row objects (must have id property)
   */
  const expandAll = useCallback((data) => {
    if (!allowMultiple) {
      console.warn('expandAll called but allowMultiple is false');
      return;
    }
    
    setExpandedRows(prev => {
      const newExpanded = new Set(prev);
      const newIds = [];
      
      data.forEach(row => {
        if (row.id && !newExpanded.has(row.id)) {
          newExpanded.add(row.id);
          newIds.push(row.id);
        }
      });
      
      // Call onExpand for newly expanded rows
      if (onExpand && newIds.length > 0) {
        newIds.forEach(rowId => onExpand(rowId));
      }
      
      return newExpanded;
    });
  }, [allowMultiple, onExpand]);

  /**
   * Check if a specific row is expanded
   * @param {string|number} rowId - Unique identifier for the row
   * @returns {boolean} True if row is expanded
   */
  const isRowExpanded = useCallback((rowId) => {
    return expandedRows.has(rowId);
  }, [expandedRows]);

  /**
   * Get count of expanded rows
   * @returns {number} Number of currently expanded rows
   */
  const expandedCount = useMemo(() => {
    return expandedRows.size;
  }, [expandedRows]);

  /**
   * Get array of expanded row IDs
   * @returns {Array} Array of expanded row IDs
   */
  const expandedRowIds = useMemo(() => {
    return Array.from(expandedRows);
  }, [expandedRows]);

  /**
   * Check if any rows are expanded
   * @returns {boolean} True if at least one row is expanded
   */
  const hasExpandedRows = useMemo(() => {
    return expandedRows.size > 0;
  }, [expandedRows]);

  return {
    // Primary state
    expandedRows,           // Set of expanded row IDs (for internal use)
    
    // Control functions
    toggleRow,              // (rowId) => void - Toggle specific row
    expandRow,              // (rowId) => void - Expand specific row
    collapseRow,            // (rowId) => void - Collapse specific row
    collapseAll,            // () => void - Collapse all rows
    expandAll,              // (data) => void - Expand all rows from data
    
    // Query functions
    isRowExpanded,          // (rowId) => boolean - Check if row is expanded
    expandedCount,          // number - Count of expanded rows
    expandedRowIds,         // Array - IDs of expanded rows
    hasExpandedRows,        // boolean - True if any rows expanded
    
    // Configuration (for debugging/introspection)
    allowMultiple,          // boolean - Current allowMultiple setting
  };
}