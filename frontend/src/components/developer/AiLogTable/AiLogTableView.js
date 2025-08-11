// AiLogTableView - UPDATED to use FilterSelectGroup and existing Pagination
// Dramatically simplified by leveraging existing UI components
// All manual filter/sort UI replaced with FilterSelectGroup components

import React, { useMemo } from 'react';
import { 
  ExpandableTable,
  useExpandableRows,
  EmptyState,
  EMPTY_STATE_PRESETS,
  Card,
  CardSection,
  LoadingSpinner,
  FilterSelectGroup,
  Pagination,
  Button
} from '../../../shared/ui/index.js';
import LlmLogDetails from './LlmLogDetails.js';
import ImageLogDetails from './ImageLogDetails.js';

/**
 * AiLogTableView - Presentational component for AI generation logs
 * Now uses FilterSelectGroup and existing Pagination component
 * @param {object} props - Component props
 * @param {Array} props.logs - Array of generation logs
 * @param {number} props.count - Total number of logs
 * @param {object} props.filterOptions - Filter options for FilterSelectGroup
 * @param {object} props.sortOptions - Sort options for FilterSelectGroup
 * @param {object} props.filters - Current filter values
 * @param {object} props.sortValues - Current sort values
 * @param {number} props.limit - Items per page
 * @param {object} props.pagination - Pagination state object
 * @param {boolean} props.isLoading - Loading state
 * @param {boolean} props.isError - Error state
 * @param {object} props.error - Error object
 * @param {boolean} props.isLoadingOptions - Loading options state
 * @param {Function} props.onFilterChange - Filter change handler
 * @param {Function} props.onSortChange - Sort change handler
 * @param {Function} props.onLimitChange - Limit change handler
 * @param {Function} props.onRefresh - Refresh handler
 * @param {Function} props.onClearFilters - Clear filters handler
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} AiLogTableView component
 */
function AiLogTableView({
  logs = [],
  count = 0,
  filterOptions = {},
  sortOptions = {},
  filters = {},
  sortValues = {},
  limit = 20,
  pagination = null,
  isLoading = false,
  isError = false,
  error = null,
  isLoadingOptions = false,
  onFilterChange = null,
  onSortChange = null,
  onLimitChange = null,
  onRefresh = null,
  onClearFilters = null,
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
      width: '8%',
      render: (value) => (
        <span className="log-id" title={value}>
          #{value.toString().slice(-6)}
        </span>
      )
    },
    { 
      key: 'generationType', 
      header: 'Type', 
      width: '10%'
    },
    { 
      key: 'promptType', 
      header: 'Prompt Type', 
      width: '20%' 
    },
    { 
      key: 'promptName', 
      header: 'Prompt Name', 
      width: '20%' 
    },
    { 
      key: 'status', 
      header: 'Status', 
      width: '12%'
    },
    { 
      key: 'durationSeconds', 
      header: 'Duration', 
      width: '10%',
      render: (value) => value ? `${value}s` : 'N/A'
    },
    { 
      key: 'generationAttempt', 
      header: 'Attempt', 
      width: '10%',
      render: (value, log) => {
        if (log.generationAttempt && log.maxAttempts) {
          return `${log.generationAttempt}/${log.maxAttempts}`;
        }
        return 'N/A';
      }
    },
    { 
      key: 'startTime', 
      header: 'Date', 
      width: '10%',
      render: (value) => value ? new Date(value).toLocaleDateString() : 'N/A'
    },
  ], []);

  // Expanded content renderer
  const renderExpandedContent = (log) => {
    if (log.generationType === 'llm') {
      return <LlmLogDetails log={log} />;
    } else if (log.generationType === 'image') {
      return <ImageLogDetails log={log} />;
    }
    return (
      <div style={{ padding: '16px', color: 'var(--text-dim)' }}>
        No details available for this log type.
      </div>
    );
  };

  // Don't render anything if options are still loading
  if (isLoadingOptions) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <LoadingSpinner size="md" />
        <p style={{ marginTop: '10px', color: 'var(--text-dim)' }}>Loading filter options...</p>
      </div>
    );
  }

  return (
    <div className={`ai-log-table ${className}`} style={style}>
      
      {/* Filter and Sort Controls */}
      <Card size='lg'>
        <CardSection type="header" title="Generation Logs"/>
        <div type="content" style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '20px' 
        }}>
          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={onRefresh}
              disabled={isLoading}
            >
              🔄 Refresh
            </Button>
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={onClearFilters}
            >
              🗑️ Clear Filters
            </Button>
          </div>

          {/* Sort - Using FilterSelectGroup as SelectGroup */}
          <div>
            <FilterSelectGroup
              filterOptions={sortOptions}
              values={sortValues}
              onChange={onSortChange}
              layout="horizontal"
              customLabels={{
                field: 'Sort Field',
                order: 'Sort Order'
              }}
            />
          </div>

          {/* Filters - Using FilterSelectGroup */}
          <div>
            <strong>Filters:</strong>
            <FilterSelectGroup
              filterOptions={filterOptions}
              values={filters}
              onChange={onFilterChange}
              layout="horizontal"
            />
          </div>

        </div>
        {/* Pagination (Top) */}
        {logs.length > 0 && pagination && (
          <Pagination
            pagination={pagination}
            itemName="logs"
            layout="full"
            currentLimit={limit}
            onLimitChange={onLimitChange}
            itemsPerPageOptions={[10, 20, 50, 100]}
            style={{ marginBottom: '20px' }}
          />
        )}

        {/* Main Table */}
        {isError ? (
          <Card>
            <CardSection type="content">
              <div style={{ color: 'var(--color-red-intense)', padding: '1rem', textAlign: 'center' }}>
                <strong>Error:</strong> {error?.message || 'Failed to load generation logs'}
              </div>
            </CardSection>
          </Card>
        ) : isLoading ? (
            <div style={{ padding: '50px', textAlign: 'center' }}>
              <LoadingSpinner size="screen" />
            </div>
        ) : logs.length === 0 ? (
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
            emptyMessage={isLoading ? "Loading..." : "No logs found"}
            size="sm"
            striped
            hover
            loading={isLoading}
          />
        )}

        {/* Pagination (Bottom) */}
        {logs.length > 0 && pagination && (
          <Pagination
            pagination={pagination}
            itemName="logs"
            layout="simple"
            style={{ marginTop: '20px' }}
          />
        )}
        </Card>
    </div>
  );
}

export default AiLogTableView;