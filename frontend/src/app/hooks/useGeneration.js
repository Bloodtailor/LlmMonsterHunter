// Enhanced Generation Hooks - COMPLETELY GENERIC VERSION
// Hook derives all filter names from backend options - no hardcoded filter knowledge!
// Uses existing usePagination hook and works with FilterSelectGroup component
// Can work with any backend that provides filterOptions, regardless of filter names

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import { usePagination } from '../../shared/ui/Pagination/usePagination.js';
import * as generationApi from './../../api/services/generation.js';

/**
 * Enhanced hook for managing generation logs with built-in filtering, sorting, and pagination
 * Uses existing usePagination hook and works perfectly with FilterSelectGroup component
 * 
 * COMPLETELY GENERIC - derives filter names from backend options, no hardcoded filter names!
 * 
 * How it works:
 * 1. Loads filterOptions from backend (contains filter names + possible values)
 * 2. Dynamically initializes filters state with all filters set to 'all'
 * 3. clearFilters() dynamically resets based on available filter names
 * 4. Can work with ANY backend that provides filterOptions structure
 */
export function useGenerationLogs(options = {}) {
  const {
    autoLoad = true,
    defaultLimit = 20
  } = options;

  // ✨ Core data fetching using useAsyncState pattern
  const logsApi = useAsyncState(generationApi.getGenerationLogs);
  const optionsApi = useAsyncState(generationApi.getGenerationLogOptions);

  // ===== SIMPLE STATE MANAGEMENT =====
  const [filters, setFilters] = useState({});
  const [sortValues, setSortValues] = useState({
    field: 'id',
    order: 'desc'
  });
  const [limit, setLimit] = useState(defaultLimit);

  // ✨ Use existing usePagination hook
  const pagination = usePagination({
    limit,
    total: logsApi.data.count,
    initialPage: 1
  });

  // ===== AUTO-LOAD OPTIONS AND INITIALIZE FILTERS =====
  useEffect(() => {
    optionsApi.execute();
  }, [optionsApi.execute]);

  // Initialize filters when options load (completely dynamic!)
  // This makes the hook work with ANY backend that provides filterOptions
  useEffect(() => {
    if (optionsApi.data.filterOptions && Object.keys(filters).length === 0) {
      const initialFilters = {};
      Object.keys(optionsApi.data.filterOptions).forEach(filterName => {
        initialFilters[filterName] = 'all';
      });
      setFilters(initialFilters);
    }
  }, [optionsApi.data.filterOptions, filters]);

  // ===== ENHANCED OPTIONS FOR FilterSelectGroup =====
  const filterOptions = useMemo(() => {
    if (!optionsApi.data.filterOptions) return {};

    const enhanced = {};
    // Add "all" option to each filter array for FilterSelectGroup
    Object.entries(optionsApi.data.filterOptions).forEach(([key, values]) => {
      enhanced[key] = ['all', ...(values || [])];
    });
    return enhanced;
  }, [optionsApi.data.filterOptions]);

  // Sort options formatted for FilterSelectGroup
  const sortOptions = useMemo(() => {
    if (!optionsApi.data.sortOptions) {
      return {
        field: ['id', 'generation_type', 'status', 'start_time'],
        order: ['desc', 'asc']
      };
    }

    return {
      field: optionsApi.data.sortOptions.fields || ['id'],
      order: optionsApi.data.sortOptions.orders || ['desc', 'asc']
    };
  }, [optionsApi.data.sortOptions]);

  // ===== LOAD DATA WHEN PARAMS CHANGE =====
  const loadData = useCallback(() => {
    const params = {
      limit,
      offset: pagination.currentOffset
    };

    // Add non-"all" filters (completely dynamic!)
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'all') {
        params[key] = value;
      }
    });

    // Add sort
    params.sortBy = sortValues.field;
    params.sortOrder = sortValues.order;

    logsApi.execute(params);
  }, [logsApi.execute, limit, pagination.currentOffset, filters, sortValues]);

  // Auto-load when dependencies change (wait for filters to be initialized)
  useEffect(() => {
    if (autoLoad && optionsApi.data.filterOptions && Object.keys(filters).length > 0) {
      loadData();
    }
  }, [loadData, autoLoad, optionsApi.data.filterOptions, filters]);

  // ===== SIMPLE EVENT HANDLERS =====
  const handleFilterChange = useCallback((fieldName, newValue, updatedValues) => {
    setFilters(updatedValues);
    pagination.firstPage(); // Reset to first page
  }, [pagination]);

  const handleSortChange = useCallback((fieldName, newValue, updatedValues) => {
    setSortValues(updatedValues);
    pagination.firstPage(); // Reset to first page
  }, [pagination]);

  const handleLimitChange = useCallback((newLimit) => {
    setLimit(newLimit);
    pagination.setLimit(newLimit);
  }, [pagination]);

  const refresh = useCallback(() => {
    loadData();
  }, [loadData]);

  const clearFilters = useCallback(() => {
    // Dynamically reset all filters to 'all' - works with any filter set!
    if (optionsApi.data.filterOptions) {
      const clearedFilters = {};
      Object.keys(optionsApi.data.filterOptions).forEach(filterName => {
        clearedFilters[filterName] = 'all';
      });
      setFilters(clearedFilters);
      pagination.firstPage();
    }
  }, [pagination, optionsApi.data.filterOptions]);

  return {
    // ===== DATA =====
    logs: logsApi.data.logs || [],
    count: logsApi.data.count || 0,

    // ===== OPTIONS (ready for FilterSelectGroup) =====
    filterOptions,  // Enhanced with "all" options
    sortOptions,    // Formatted for FilterSelectGroup

    // ===== CURRENT STATE =====
    filters,        // Current filter values
    sortValues,     // Current sort values
    limit,          // Current page size

    // ===== PAGINATION (from usePagination hook) =====
    pagination,

    // ===== STATE FLAGS =====
    isLoading: logsApi.isLoading,
    isError: logsApi.isError,
    error: logsApi.error,
    isLoadingOptions: optionsApi.isLoading,

    // ===== SIMPLE HANDLERS (ready for FilterSelectGroup) =====
    handleFilterChange,  // For FilterSelectGroup onChange
    handleSortChange,    // For FilterSelectGroup onChange
    handleLimitChange,   // For Pagination onLimitChange
    refresh,
    clearFilters,

    // ===== DEBUG =====
    rawResponse: logsApi.data._raw,
    rawOptionsResponse: optionsApi.data._raw
  };
}