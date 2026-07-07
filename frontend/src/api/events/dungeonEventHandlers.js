// Dungeon Event Handlers - External (non-React) event handling
// Transforms dungeon domain SSE events and broadcasts to event subscribers.
// dungeon.monster_revealed announces a PRE-EXISTING monster staged into
// the current encounter (returning monsters and blend-ins) - new monsters
// announce themselves via monster.created instead.

import { transformMonster } from "../transformers/monsters.js";
import { broadcastEvent } from "../core/eventBroadcast.js";

export const dungeonEventHandlers = {
  'dungeon.monster_revealed': (eventData) => {
    const transformedData = {
      monster: transformMonster(eventData.monster)
    };
    broadcastEvent('dungeonMonsterRevealed', transformedData);
  }
};
