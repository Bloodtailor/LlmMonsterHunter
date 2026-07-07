// Monster Event Handlers - External (non-React) event handling
// Transforms monster domain SSE events and broadcasts to event subscribers
// These are facts about the game world (monster exists, has art, has ability),
// not machinery progress - subscribe to react the moment they become true

import { transformMonster, transformAbility, transformMemory, transformEvolution } from "../transformers/monsters.js";
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

  // Staged generation filled in more of an existing monster (persona, story)
  'monster.updated': (eventData) => {
    const transformedData = {
      monster: transformMonster(eventData.monster)
    };
    broadcastEvent('monsterUpdated', transformedData);
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
  },

  // The monster recorded a new permanent memory of the party
  'monster.memory_added': (eventData) => {
    const transformedData = {
      monsterId: eventData.monster_id || null,
      memory: transformMemory(eventData.memory)
    };
    broadcastEvent('monsterMemoryAdded', transformedData);
  },

  // The evolution ceremony's transform moment - identity, stats, and
  // rarity just flipped in place; the record carries the old form
  'monster.evolved': (eventData) => {
    const transformedData = {
      monster: transformMonster(eventData.monster),
      evolution: transformEvolution(eventData.evolution)
    };
    broadcastEvent('monsterEvolved', transformedData);
  }
};
