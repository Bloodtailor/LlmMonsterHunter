// Monster Event Handlers - External (non-React) event handling
// Transforms monster domain SSE events and broadcasts to event subscribers
// These are facts about the game world (monster exists, has art, has ability),
// not machinery progress - subscribe to react the moment they become true

import { transformMonster, transformAbility } from "../transformers/monsters.js";
import { broadcastEvent } from "../core/eventBroadcast.js";

/**
 * Monster Event Handlers - External event processing system
 * Each handler transforms event data and broadcasts to subscribers
 */
export const monsterEventHandlers = {
  'monster.created': (eventData) => {
    const transformedData = {
      monster: transformMonster(eventData.monster)
    };
    broadcastEvent('monsterCreated', transformedData);
  },

  'monster.ability_added': (eventData) => {
    const transformedData = {
      monsterId: eventData.monster_id || null,
      ability: transformAbility(eventData.ability)
    };
    broadcastEvent('monsterAbilityAdded', transformedData);
  },

  'monster.art_ready': (eventData) => {
    const transformedData = {
      monsterId: eventData.monster_id || null,
      imagePath: eventData.image_path || null
    };
    broadcastEvent('monsterArtReady', transformedData);
  }
};
