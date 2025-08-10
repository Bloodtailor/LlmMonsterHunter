// AiLogTableContainer - Data management container for AI generation logs table
// Handles data fetching, state management, filtering, sorting, and pagination
// Passes everything as props to AiLogTableView for clean separation of concerns

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { useGenerationLogs } from '../../../app/hooks/useGeneration.js';
import { usePagination } from '../../../shared/ui/Pagination/usePagination.js';
import AiLogTableView from './AiLogTableView.js';

/**
 * AiLogTableContainer - Data management container for AI logs table
 * @param {object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} AiLogTableContainer component
 */
function AiLogTableContainer({ className = '', style = {} }) {
  // Filter and display state
  const [filterType, setFilterType] = useState('all'); // all, llm, image
  const [filterStatus, setFilterStatus] = useState('all'); // all, completed, failed, running
  const [limit, setLimit] = useState(20);
  const [sortField, setSortField] = useState('startTime');
  const [sortDirection, setSortDirection] = useState('desc');

  // Generation logs data hook
  const { logs: generationLogs, logsCount, isLoading: loadingLogs, loadLogs } = useGenerationLogs();

  // Load logs on mount and when dependencies change
  useEffect(() => {
    loadLogs({
      limit: 100, // Load more logs for client-side filtering
      type: filterType !== 'all' ? filterType : undefined,
      status: filterStatus !== 'all' ? filterStatus : undefined
    });
  }, [loadLogs, filterType, filterStatus]);

  // Filtered and sorted logs (client-side processing)
  const filteredLogs = useMemo(() => {
    let filtered = generationLogs || [];

    return filtered;
  }, [generationLogs, sortField, sortDirection]);

  // Pagination
  const pagination = usePagination({ 
    limit, 
    total: filteredLogs.length 
  });

  // Get paginated logs
  const paginatedLogs = useMemo(() => {
    return filteredLogs.slice(
      pagination.currentOffset,
      pagination.currentOffset + pagination.limit
    );
  }, [filteredLogs, pagination.currentOffset, pagination.limit]);

  // Event handlers
  const handleFilterTypeChange = useCallback((newType) => {
    setFilterType(newType);
    pagination.firstPage(); // Reset to first page when filtering changes
  }, [pagination]);

  const handleFilterStatusChange = useCallback((newStatus) => {
    setFilterStatus(newStatus);
    pagination.firstPage(); // Reset to first page when filtering changes
  }, [pagination]);

  const handleSortChange = useCallback((field, direction) => {
    setSortField(field);
    setSortDirection(direction);
    pagination.firstPage(); // Reset to first page when sorting changes
  }, [pagination]);

  const handleLimitChange = useCallback((newLimit) => {
    setLimit(newLimit);
    pagination.firstPage(); // Reset to first page when limit changes
  }, [pagination]);

  const handleRefresh = useCallback(() => {
    loadLogs({
      limit: 100,
      type: filterType !== 'all' ? filterType : undefined,
      status: filterStatus !== 'all' ? filterStatus : undefined,
      promptName: 'user_request'
    });
  }, [loadLogs, filterType, filterStatus]);

  // Pass everything to the view component
  return (
    <AiLogTableView
      logs={paginatedLogs}
      isLoading={loadingLogs}
      filterType={filterType}
      filterStatus={filterStatus}
      sortField={sortField}
      sortDirection={sortDirection}
      limit={limit}
      pagination={pagination}
      onFilterTypeChange={handleFilterTypeChange}
      onFilterStatusChange={handleFilterStatusChange}
      onSortChange={handleSortChange}
      onLimitChange={handleLimitChange}
      onRefresh={handleRefresh}
      className={className}
      style={style}
    />
  );
}

export default AiLogTableContainer;