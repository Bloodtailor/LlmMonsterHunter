// Game-State Event Handlers - the world itself changing shape
// Transforms SSE events and broadcasts to state stores and subscribers.
// Mirrors backend/core/events/game_state_events.py. The wipe event is
// how app-level roster state (PartyContext) empties the moment the
// world does, instead of waiting for a page refresh.

import { broadcastEvent } from '../core/eventBroadcast.js';

export const gameStateEventHandlers = {
  'game.world_erased': (eventData) => {
    const transformedData = {
      deletedRows: eventData.deleted_rows || {},
      timestamp: eventData.timestamp || null,
    };
    broadcastEvent('worldErased', transformedData);
  },

  // The backend reshaped the roster on its own (a new follower,
  // possibly auto-seated into an open party slot) - PartyContext
  // refetches so every party panel shows the newcomer immediately
  'game.party_updated': (eventData) => {
    const transformedData = {
      monsterId: eventData.monster_id ?? null,
      monsterName: eventData.monster_name ?? null,
      joinedParty: eventData.joined_party ?? false,
      partyIds: eventData.party_ids || [],
    };
    broadcastEvent('partyUpdated', transformedData);
  },
};
