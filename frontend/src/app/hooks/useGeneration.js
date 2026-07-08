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
  const { autoLoad = true, defaultLimit = 20 } = options;

  // ✨ Core data fetching using useAsyncState pattern
  const logsApi = useAsyncState(generationApi.getGenerationLogs);
  const optionsApi = useAsyncState(generationApi.getGenerationLogOptions);

  // Destructured because effects/callbacks below depend on these functions:
  // useAsyncState keeps execute referentially stable, and depending on it
  // directly (instead of on the whole logsApi/optionsApi object, which is
  // rebuilt every render) is what lets the dependency arrays stay honest.
  const { execute: fetchLogs } = logsApi;
  const { execute: fetchOptions } = optionsApi;

  // ===== SIMPLE STATE MANAGEMENT =====
  // filters starts as null, NOT {} — "filter names unknown until options
  // arrive" must be distinguishable from "initialized", or the init effect
  // below could re-fire forever (that exact loop used to crash this hook
  // with "Maximum update depth exceeded"). Consumers never see the null:
  // the return block substitutes {}.
  const [filters, setFilters] = useState(null);
  const [sortValues, setSortValues] = useState({
    field: 'id',
    order: 'desc',
  });
  const [limit, setLimit] = useState(defaultLimit);

  // ✨ Use existing usePagination hook
  const pagination = usePagination({
    limit,
    total: logsApi.data.count,
    initialPage: 1,
  });

  // Only these pieces of pagination participate in dependency arrays — the
  // pagination object itself is rebuilt every render, so depending on it
  // would recreate every callback on every render.
  const { currentOffset, firstPage, setLimit: setPaginationLimit } = pagination;

  // ===== AUTO-LOAD OPTIONS AND INITIALIZE FILTERS =====
  useEffect(() => {
    fetchOptions();
  }, [fetchOptions]);

  // Initialize filters when options load (completely dynamic!)
  // This makes the hook work with ANY backend that provides filterOptions.
  // Gated on isSuccess rather than on the data: before the fetch resolves,
  // data holds placeholder defaults that must not be mistaken for real
  // options. The functional update returns the existing state untouched once
  // initialized, so this effect cannot re-trigger itself.
  useEffect(() => {
    if (!optionsApi.isSuccess) return;
    const loadedFilterOptions = optionsApi.data.filterOptions || {};
    setFilters((currentFilters) => {
      if (currentFilters !== null) return currentFilters;
      const initialFilters = {};
      Object.keys(loadedFilterOptions).forEach((filterName) => {
        initialFilters[filterName] = 'all';
      });
      return initialFilters;
    });
  }, [optionsApi.isSuccess, optionsApi.data.filterOptions]);

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
        order: ['desc', 'asc'],
      };
    }

    return {
      field: optionsApi.data.sortOptions.fields || ['id'],
      order: optionsApi.data.sortOptions.orders || ['desc', 'asc'],
    };
  }, [optionsApi.data.sortOptions]);

  // ===== LOAD DATA WHEN PARAMS CHANGE =====
  const loadData = useCallback(() => {
    const params = {
      limit,
      offset: currentOffset,
    };

    // Add non-"all" filters (completely dynamic!)
    // filters can still be null if this is called before options load
    // (e.g. refresh() clicked early) — treat that as "no filters"
    Object.entries(filters ?? {}).forEach(([key, value]) => {
      if (value && value !== 'all') {
        params[key] = value;
      }
    });

    // Add sort
    params.sortBy = sortValues.field;
    params.sortOrder = sortValues.order;

    fetchLogs(params);
  }, [fetchLogs, limit, currentOffset, filters, sortValues]);

  // Auto-load when dependencies change (wait for filters to be initialized,
  // so the first fetch isn't duplicated a moment later by the filter init)
  useEffect(() => {
    if (autoLoad && filters !== null) {
      loadData();
    }
  }, [autoLoad, filters, loadData]);

  // ===== SIMPLE EVENT HANDLERS =====
  const handleFilterChange = useCallback(
    (fieldName, newValue, updatedValues) => {
      setFilters(updatedValues);
      firstPage(); // Reset to first page
    },
    [firstPage],
  );

  const handleSortChange = useCallback(
    (fieldName, newValue, updatedValues) => {
      setSortValues(updatedValues);
      firstPage(); // Reset to first page
    },
    [firstPage],
  );

  const handleLimitChange = useCallback(
    (newLimit) => {
      setLimit(newLimit);
      setPaginationLimit(newLimit);
    },
    [setPaginationLimit],
  );

  const refresh = useCallback(() => {
    loadData();
  }, [loadData]);

  const clearFilters = useCallback(() => {
    // Dynamically reset all filters to 'all' - works with any filter set!
    if (optionsApi.data.filterOptions) {
      const clearedFilters = {};
      Object.keys(optionsApi.data.filterOptions).forEach((filterName) => {
        clearedFilters[filterName] = 'all';
      });
      setFilters(clearedFilters);
      firstPage();
    }
  }, [optionsApi.data.filterOptions, firstPage]);

  return {
    // ===== DATA =====
    logs: logsApi.data.logs || [],
    count: logsApi.data.count || 0,

    // ===== OPTIONS (ready for FilterSelectGroup) =====
    filterOptions, // Enhanced with "all" options
    sortOptions, // Formatted for FilterSelectGroup

    // ===== CURRENT STATE =====
    filters: filters ?? {}, // Current filter values (always an object for consumers)
    sortValues, // Current sort values
    limit, // Current page size

    // ===== PAGINATION (from usePagination hook) =====
    pagination,

    // ===== STATE FLAGS =====
    isLoading: logsApi.isLoading,
    isError: logsApi.isError,
    error: logsApi.error,
    isLoadingOptions: optionsApi.isLoading,

    // ===== SIMPLE HANDLERS (ready for FilterSelectGroup) =====
    handleFilterChange, // For FilterSelectGroup onChange
    handleSortChange, // For FilterSelectGroup onChange
    handleLimitChange, // For Pagination onLimitChange
    refresh,
    clearFilters,

    // ===== DEBUG =====
    rawResponse: logsApi.data._raw,
    rawOptionsResponse: optionsApi.data._raw,
  };
}
