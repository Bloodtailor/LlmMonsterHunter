// AiLogTableView - Pure presentational component for AI generation logs table
// Renders ExpandableTable with controls, pagination, and expanded content
// No data fetching or state management - all props come from container

import React, { useMemo, useCallback } from 'react';
import { 
  ExpandableTable,
  useExpandableRows,
  Select,
  EmptyState,
  EMPTY_STATE_PRESETS,
  Card,
  LoadingSpinner,
  StatusBadge,
  Badge
} from '../../../shared/ui/index.js';
import FullPagination, { PAGINATION_LAYOUTS } from '../../../shared/ui/Pagination/PaginationPresets.js';
import LlmLogDetails from './LlmLogDetails.js';
import ImageLogDetails from './ImageLogDetails.js';

/**
 * AiLogTableView - Presentational component for AI generation logs
 * @param {object} props - Component props
 * @param {Array} props.logs - Array of generation logs
 * @param {boolean} props.isLoading - Loading state
 * @param {string} props.filterType - Current type filter
 * @param {string} props.filterStatus - Current status filter
 * @param {string} props.sortField - Current sort field
 * @param {string} props.sortDirection - Current sort direction
 * @param {number} props.limit - Items per page
 * @param {object} props.pagination - Pagination state object
 * @param {Function} props.onFilterTypeChange - Type filter change handler
 * @param {Function} props.onFilterStatusChange - Status filter change handler
 * @param {Function} props.onSortChange - Sort change handler
 * @param {Function} props.onLimitChange - Limit change handler
 * @param {Function} props.onRefresh - Refresh handler
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} AiLogTableView component
 */
function AiLogTableView({
  logs = [],
  isLoading = false,
  filterType = 'all',
  filterStatus = 'all', 
  sortField = 'startTime',
  sortDirection = 'desc',
  limit = 20,
  pagination = null,
  onFilterTypeChange = null,
  onFilterStatusChange = null,
  onSortChange = null,
  onLimitChange = null,
  onRefresh = null,
  className = '',
  style = {}
}) {

  // Expandable table functionality
  const expandableRows = useExpandableRows({
    allowMultiple: false,
    defaultExpanded: []
  });

  // Column definitions for the table
  const columns = useMemo(() => [
    { 
      key: 'id', 
      header: 'ID', 
      width: '10%',
      render: (value) => (
        <span className="log-id" title={value}>
          #{value.toString().slice(-6)}
        </span>
      )
    },
    { 
      key: 'generationType', 
      header: 'Type', 
      width: '12%',
    },
    { 
      key: 'promptType', 
      header: 'Prompt Type', 
      width: '15%' 
    },
    { 
      key: 'promptName', 
      header: 'Prompt Name', 
      width: '20%' 
    },
    { 
      key: 'status', 
      header: 'Status', 
      width: '12%',
    },
    { 
      key: 'durationSeconds', 
      header: 'Duration', 
      width: '10%',
      render: (value) => value ? `${value}s` : '-'
    },
    { 
      key: 'generationAttempt', 
      header: 'Attempt', 
      width: '8%',
      render: (value, row) => `${value}/${row.maxAttempts}`
    },
    { 
      key: 'startTime', 
      header: 'Date', 
      width: '6%',
      render: (value) => value ? new Date(value).toLocaleDateString() : '-'
    },
    { 
      key: 'startTime', 
      header: 'Time', 
      width: '7%',
      render: (value) => value ? new Date(value).toLocaleTimeString([],{
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      }) : '-'
    }
  ], []);

  // Render expanded content based on generation type
  const renderExpandedContent = useCallback((log) => {
    if (log.generationType === 'llm') {
      return <LlmLogDetails log={log} />;
    } else if (log.generationType === 'image') {
      return <ImageLogDetails log={log} />;
    }
    return (
      <div style={{ padding: '16px', color: 'var(--text-dim)' }}>
        No additional details available for this generation type.
      </div>
    );
  }, []);

  // Handle sort change
  const handleSortChange = useCallback((e) => {
    const [field, direction] = e.target.value.split('-');
    onSortChange?.(field, direction);
  }, [onSortChange]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    onRefresh?.();
    expandableRows.collapseAll();
  }, [onRefresh, expandableRows]);

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <LoadingSpinner size="section" type="pulse" />
        <p style={{ marginTop: '16px', color: 'var(--text-dim)' }}>
          Loading generation logs...
        </p>
      </div>
    );
  }

  return (
    <div className={`ai-log-table ${className}`} style={style}>
      {/* Controls */}
      <Card>
        <div style={{
          display: 'flex',
          flexDirection: 'row',
          gap: '12px',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          <label style={{ minWidth: '120px' }}>
            Type:
            <Select
              value={filterType}
              onChange={(e) => onFilterTypeChange?.(e.target.value)}
              options={[
                { value: 'all', label: 'All Types' },
                { value: 'llm', label: 'LLM Only' },
                { value: 'image', label: 'Image Only' }
              ]}
            />
          </label>
          
          <label style={{ minWidth: '120px' }}>
            Status:
            <Select
              value={filterStatus}
              onChange={(e) => onFilterStatusChange?.(e.target.value)}
              options={[
                { value: 'all', label: 'All Status' },
                { value: 'completed', label: 'Completed' },
                { value: 'failed', label: 'Failed' },
                { value: 'running', label: 'Running' }
              ]}
            />
          </label>

          <label style={{ minWidth: '120px' }}>
            Sort:
            <Select
              value={`${sortField}-${sortDirection}`}
              onChange={handleSortChange}
              options={[
                { value: 'startTime-desc', label: 'Newest First' },
                { value: 'startTime-asc', label: 'Oldest First' },
                { value: 'durationSeconds-desc', label: 'Longest Duration' },
                { value: 'durationSeconds-asc', label: 'Shortest Duration' },
                { value: 'status-asc', label: 'Status A-Z' }
              ]}
            />
          </label>

          <button
            onClick={handleRefresh}
            style={{
              padding: '8px 16px',
              background: 'var(--background-light)',
              border: '1px solid var(--background-dark)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-light)',
              cursor: 'pointer'
            }}
          >
            🔄 Refresh
          </button>
        </div>
      </Card>

      {/* Pagination (Top) */}
      {logs.length > 0 && pagination && (
        <FullPagination
          pagination={pagination}
          itemName="logs"
          itemsPerPageOptions={[10, 20, 50, 100]}
          currentLimit={limit}
          onLimitChange={onLimitChange}
          layout={PAGINATION_LAYOUTS.FULL}
        />
      )}

      {/* Expandable Table */}
      {logs.length === 0 ? (
        <EmptyState
          {...EMPTY_STATE_PRESETS.NO_DATA}
          title="No Generation Logs"
          message="No logs match your current filters."
          size="lg"
          style={{ margin: '40px 0' }}
        />
      ) : (
        <ExpandableTable
          columns={columns}
          data={logs}
          expandableRows={expandableRows}
          renderExpandedContent={renderExpandedContent}
          emptyMessage="No logs found"
          size="sm"
          striped
          hover
        />
      )}

      {/* Pagination (Bottom) */}
      {logs.length > 0 && pagination && (
        <FullPagination
          pagination={pagination}
          itemName="logs"
          currentLimit={limit}
          onLimitChange={onLimitChange}
          layout={PAGINATION_LAYOUTS.DEFAULT}
        />
      )}
    </div>
  );
}

export default AiLogTableView;