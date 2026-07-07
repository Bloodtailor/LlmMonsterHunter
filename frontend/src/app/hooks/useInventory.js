// Inventory App Hooks
// Paged inventory collections that stay fresh via inventory domain events
// (acquisition and consumption trigger a refetch of the current page -
// inventory pages are small, so refetching beats patch bookkeeping)

import { useEffect, useCallback, useRef } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import { useEventSubscription } from '../../api/events/useEventSubscription.js';
import * as inventoryApi from '../../api/services/inventory.js';

/**
 * Hook for one paged inventory kind ('items' | 'cocatoks')
 * Stays live: any inventory event refetches the current page
 */
export function useInventoryCollection(kind = 'items') {
  const api = useAsyncState(inventoryApi.loadInventory);

  // Remember the last query so event-driven refetches reuse it
  const lastQuery = useRef({ kind, limit: undefined, offset: 0 });

  const load = useCallback(
    async ({ limit, offset } = {}) => {
      lastQuery.current = { kind, limit, offset };
      return await api.execute({ kind, limit, offset });
    },
    [api.execute, kind],
  );

  const reload = useCallback(() => {
    const { limit, offset } = lastQuery.current;
    api.execute({ kind, limit, offset });
  }, [api.execute, kind]);

  // The party's possessions changed - refresh whichever page is showing
  useEventSubscription('inventoryItemAdded', () => {
    if (kind === 'items') reload();
  });
  useEventSubscription('inventoryItemUpdated', () => {
    if (kind === 'items') reload();
  });
  useEventSubscription('inventoryItemConsumed', () => {
    if (kind === 'items') reload();
  });
  useEventSubscription('inventoryCocatokAdded', () => {
    if (kind === 'cocatoks') reload();
  });

  return {
    entries: api.data.entries, // Always an array
    total: api.data.total, // Always a number
    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,
    load,
    reload,
  };
}

/**
 * Hook for the usable-items list (item pickers in battle and dungeon forms)
 * Loads every item with uses left; refreshes on inventory events
 */
export function useUsableItems() {
  const { entries, load, isLoading } = useInventoryCollection('items');

  useEffect(() => {
    load({});
  }, [load]);

  return {
    items: (entries || []).filter((item) => item.usesRemaining > 0),
    isLoading,
  };
}
