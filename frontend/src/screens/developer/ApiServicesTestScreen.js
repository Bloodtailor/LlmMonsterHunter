// ApiServicesTestScreen - SIMPLIFIED VERSION using existing UI components
// Dramatically reduced code by leveraging FilterSelectGroup, Pagination, and Table components
// Clean and focused on testing the enhanced hook

import React from 'react';
import { useGenerationLogs } from '../../app/hooks/useGeneration';
import { 
  Button, 
  Card, 
  CardSection, 
  Table, 
  FilterSelectGroup, 
  LoadingSpinner,
  Pagination
} from '../../shared/ui';

function ApiServicesTestScreen() {
  // ===== SINGLE HOOK - All complexity hidden =====
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
    refresh,
    clearFilters,
    
    // Debug
    rawResponse,
    rawOptionsResponse
  } = useGenerationLogs({
    autoLoad: true,
    defaultLimit: 10
  });

  // ===== RENDER =====
  
  if (isLoadingOptions) {
    return (
      <Card>
        <CardSection type="header" title="Loading Options...">
          <LoadingSpinner size="sm" />
        </CardSection>
      </Card>
    );
  }

  return (
    <Card>
      {/* Controls */}
      <CardSection type="header" title="Enhanced useGenerationLogs Test">
        
        {/* Filters - Using existing FilterSelectGroup */}
        <div style={{ marginBottom: '1rem' }}>
          <strong>Filters:</strong>
          <FilterSelectGroup
            filterOptions={filterOptions}
            values={filters}
            onChange={handleFilterChange}
            layout="grid"
          />
        </div>

        {/* Sorts - Using FilterSelectGroup as "SelectGroup" */}
        <div style={{ marginBottom: '1rem' }}>
          <strong>Sort:</strong>
          <FilterSelectGroup
            filterOptions={sortOptions}
            values={sortValues}
            onChange={handleSortChange}
            layout="horizontal"
            customLabels={{
              field: 'Sort Field',
              order: 'Sort Order'
            }}
          />
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Button 
            variant="secondary" 
            size="sm" 
            onClick={refresh}
            disabled={isLoading}
          >
            🔄 Refresh
          </Button>
          <Button 
            variant="secondary" 
            size="sm" 
            onClick={clearFilters}
          >
            🗑️ Clear Filters
          </Button>
        </div>
      </CardSection>

      {/* Status */}
      <CardSection title="Status" type="content">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
          gap: '1rem',
          marginBottom: '1rem'
        }}>
          <div><strong>Total:</strong> {count}</div>
          <div><strong>Showing:</strong> {logs.length}</div>
          <div><strong>Page:</strong> {pagination.currentPage} of {pagination.totalPages || '?'}</div>
          <div><strong>Status:</strong> {isLoading ? 'Loading...' : 'Ready'}</div>
        </div>

        <div style={{ 
          background: 'var(--background-medium)', 
          padding: '0.5rem', 
          borderRadius: 'var(--radius-sm)',
          fontSize: 'var(--font-size-sm)'
        }}>
          <div><strong>Filters:</strong> {JSON.stringify(filters)}</div>
          <div><strong>Sort:</strong> {JSON.stringify(sortValues)}</div>
        </div>
      </CardSection>

      {/* Pagination - Using existing Pagination component */}
      <Pagination
        pagination={pagination}
        itemName="logs"
        layout="full"
        currentLimit={limit}
        onLimitChange={handleLimitChange}
        itemsPerPageOptions={[5, 10, 20, 50]}
      />

      {/* Data Table - Using existing Table component */}
      <CardSection title="Generation Logs" type="content">
        {isError ? (
          <div style={{ color: 'var(--color-red-intense)', padding: '1rem' }}>
            <strong>Error:</strong> {error?.message || 'Failed to load logs'}
          </div>
        ) : (
          <Table
            columns={[
              { key: 'id', header: 'ID', width: '10%' },
              { key: 'generationType', header: 'Type', width: '12%' },
              { key: 'promptType', header: 'Prompt Type', width: '18%' },
              { key: 'promptName', header: 'Prompt Name', width: '20%' },
              { key: 'status', header: 'Status', width: '12%' },
              { key: 'durationSeconds', header: 'Duration', width: '12%' },
              { key: 'startTime', header: 'Date', width: '16%' },
            ]}
            data={logs.map(log => ({
              id: log.id ? `#${log.id.toString().slice(-6)}` : 'N/A',
              generationType: log.generationType || 'N/A',
              promptType: log.promptType || 'N/A',
              promptName: log.promptName || 'N/A',
              status: log.status || 'N/A',
              durationSeconds: log.durationSeconds ? `${log.durationSeconds}s` : 'N/A',
              startTime: log.startTime ? new Date(log.startTime).toLocaleDateString() : 'N/A',
            }))}
            maxHeight="400px"
            emptyMessage={isLoading ? "Loading..." : "No logs found"}
            loading={isLoading}
          />
        )}
      </CardSection>

      {/* Debug Info */}
      <CardSection title="Debug Information" type="content">
        <div style={{ fontSize: 'var(--font-size-sm)' }}>
          <div style={{ marginBottom: '0.5rem' }}>
            <strong>Options Response:</strong>
            <pre style={{ 
              background: 'var(--background-dark)', 
              padding: '0.5rem', 
              borderRadius: 'var(--radius-sm)',
              overflow: 'auto',
              maxHeight: '100px'
            }}>
              {JSON.stringify(rawOptionsResponse, null, 2)?.slice(0, 400)}...
            </pre>
          </div>
          
          <div>
            <strong>Data Response:</strong>
            <pre style={{ 
              background: 'var(--background-dark)', 
              padding: '0.5rem', 
              borderRadius: 'var(--radius-sm)',
              overflow: 'auto',
              maxHeight: '100px'
            }}>
              {JSON.stringify(rawResponse, null, 2)?.slice(0, 400)}...
            </pre>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default ApiServicesTestScreen;