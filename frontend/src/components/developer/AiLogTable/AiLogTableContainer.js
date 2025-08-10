// AiLogTableContainer - UPDATED to use enhanced useGenerationLogs hook
// Dramatically simplified by leveraging the new hook and existing UI components
// All manual state management replaced with hook-based approach

import React from 'react';
import { useGenerationLogs } from '../../../app/hooks/useGeneration.js';
import AiLogTableView from './AiLogTableView.js';

/**
 * AiLogTableContainer - Data management container for AI logs table
 * Now uses enhanced hook - all state management handled internally
 * @param {object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} AiLogTableContainer component
 */
function AiLogTableContainer({ className = '', style = {} }) {
  
  // ✨ All state management now handled by enhanced hook!
  const {
    // Data
    logs,
    count,
    
    // Options (ready for FilterSelectGroup)
    filterOptions,
    sortOptions,
    
    // Current state
    filters,
    sortValues,
    limit,
    
    // Pagination (from usePagination)
    pagination,
    
    // State flags
    isLoading,
    isError,
    error,
    isLoadingOptions,
    
    // Simple handlers (ready for components)
    handleFilterChange,
    handleSortChange,
    handleLimitChange,
    clearFilters,
    refresh
  } = useGenerationLogs({
    autoLoad: true,
    defaultLimit: 20
  });

  // Pass everything to the view component
  return (
    <AiLogTableView
      // Data
      logs={logs}
      count={count}
      
      // Options (ready for FilterSelectGroup)
      filterOptions={filterOptions}
      sortOptions={sortOptions}
      
      // Current state
      filters={filters}
      sortValues={sortValues}
      limit={limit}
      
      // Pagination
      pagination={pagination}
      
      // State flags
      isLoading={isLoading}
      isError={isError}
      error={error}
      isLoadingOptions={isLoadingOptions}
      
      // Event handlers
      onFilterChange={handleFilterChange}
      onSortChange={handleSortChange}
      onLimitChange={handleLimitChange}
      onClearFilters={clearFilters}
      onRefresh={refresh}
      
      // Style props
      className={className}
      style={style}
    />
  );
}

export default AiLogTableContainer;