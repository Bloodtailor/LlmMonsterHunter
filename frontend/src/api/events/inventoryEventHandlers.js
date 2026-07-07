// Inventory Event Handlers - External (non-React) event handling
// Transforms inventory domain SSE events and broadcasts to event subscribers
// Facts about the party's possessions: an item landed, was spent, or a
// victory minted a CoCaTok keepsake

import { transformItem, transformCoCaTok } from '../transformers/inventory.js';
import { broadcastEvent } from '../core/eventBroadcast.js';

export const inventoryEventHandlers = {
  'inventory.item_added': (eventData) => {
    broadcastEvent('inventoryItemAdded', {
      item: transformItem(eventData.item),
    });
  },

  'inventory.item_updated': (eventData) => {
    broadcastEvent('inventoryItemUpdated', {
      item: transformItem(eventData.item),
    });
  },

  'inventory.item_consumed': (eventData) => {
    broadcastEvent('inventoryItemConsumed', {
      itemId: eventData.item_id || null,
      name: eventData.name || null,
    });
  },

  'inventory.cocatok_added': (eventData) => {
    broadcastEvent('inventoryCocatokAdded', {
      cocatok: transformCoCaTok(eventData.cocatok),
    });
  },
};
