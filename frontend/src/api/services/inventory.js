// Inventory API Service
// Co-located: HTTP calls + transformations + defaults in one place
// 1:1 with backend routes, functions carry their own defaults for useAsyncState

import { getWithParams, get } from '../core/client.js';
import { transformInventoryEntries } from '../transformers/inventory.js';

/**
 * Load one inventory kind with server-side pagination
 * @param {object} options - Query options
 * @param {string} options.kind - 'items' | 'cocatoks' (default 'items')
 * @param {number} options.limit - Entries per page (1-1000)
 * @param {number} options.offset - Offset for pagination (0+)
 * @returns {Promise<object>} Clean transformed response with entries and pagination
 */
export async function loadInventory(options = {}) {
  const params = { kind: options.kind || 'items' };
  if (options.limit !== undefined) params.limit = options.limit;
  if (options.offset !== undefined) params.offset = options.offset;

  const response = await getWithParams('/api/inventory', params);

  return {
    kind: response.kind ?? params.kind,
    entries: transformInventoryEntries(response.entries ?? loadInventory.defaults.entries, params.kind),
    total: response.total ?? loadInventory.defaults.total,
    count: response.count ?? loadInventory.defaults.count,
    _raw: response
  };
}

loadInventory.defaults = {
  kind: 'items',
  entries: [],
  total: 0,
  count: 0
};

/**
 * Item and CoCaTok counts (for tab badges)
 * @returns {Promise<object>} Clean transformed counts
 */
export async function loadInventoryCounts() {
  const response = await get('/api/inventory/counts');

  return {
    itemCount: response.item_count ?? loadInventoryCounts.defaults.itemCount,
    cocatokCount: response.cocatok_count ?? loadInventoryCounts.defaults.cocatokCount,
    _raw: response
  };
}

loadInventoryCounts.defaults = {
  itemCount: 0,
  cocatokCount: 0
};
