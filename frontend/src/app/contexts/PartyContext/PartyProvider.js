// PartyProvider.js - The component that puts data IN the magical box
// This manages party state and provides functions to modify it
// UPDATED: Now fetches individual monster data for party members using useMonster hook

import React, { useEffect, useState, useMemo } from 'react';
import { PartyContext } from './PartyContext.js';
import { GAME_RULES } from '../../../shared/constants/constants.js';
import {
  useFollowingMonsters,
  useActiveParty,
  useSetActiveParty,
} from '../../hooks/useGameState.js';
import { useEventSubscription } from '../../../api/events/useEventSubscription.js';
import * as playerApi from '../../../api/services/player.js';

function PartyProvider({ children }) {
  // Domain hooks for game state
  const followingHook = useFollowingMonsters();
  const partyHook = useActiveParty();
  const setPartyHook = useSetActiveParty();

  // The player character rides beside the companion lists: always in
  // the party (the backend prepends it to every party read), never a
  // companion row. null on pre-character worlds - everything below
  // must keep working without one.
  const [playerMonster, setPlayerMonster] = useState(null);
  const loadPlayer = async () => {
    const { player } = await playerApi.getPlayer();
    setPlayerMonster(player);
  };

  // Load initial data
  useEffect(() => {
    followingHook.getFollowingMonsters();
    partyHook.getActiveParty();
    loadPlayer();
  }, [followingHook.getFollowingMonsters, partyHook.getActiveParty]);

  // Live copies of BOTH roster lists - growth moments, evolution
  // ceremonies, and fresh card art patch cards in place, so party panels
  // and pickers (chat, evolution) show changes without a refetch
  const [livePartyMonsters, setLivePartyMonsters] = useState(partyHook.partyMonsters);
  const [liveFollowingMonsters, setLiveFollowingMonsters] = useState(
    followingHook.followingMonsters,
  );

  useEffect(() => {
    setLivePartyMonsters(partyHook.partyMonsters);
  }, [partyHook.partyMonsters]);

  useEffect(() => {
    setLiveFollowingMonsters(followingHook.followingMonsters);
  }, [followingHook.followingMonsters]);

  const patchRosterLists = (patchMonster) => {
    setLivePartyMonsters((prev) => (prev || []).map(patchMonster));
    setLiveFollowingMonsters((prev) => (prev || []).map(patchMonster));
    setPlayerMonster((prev) => (prev ? patchMonster(prev) : prev));
  };

  // Character creation happens mid-session: the wizard's monster.created
  // is how this provider learns a player now exists
  useEventSubscription('monsterCreated', () => {
    if (!playerMonster) loadPlayer();
  });

  // The backend reshaped the roster on its own (a recruit started
  // following and may have auto-seated into an open party slot):
  // refetch both lists so every party panel shows the newcomer
  useEventSubscription('partyUpdated', () => {
    followingHook.getFollowingMonsters();
    partyHook.getActiveParty();
  });

  // New Game erased the world: empty every roster NOW (no refresh
  // needed), then refetch so the hooks' own state agrees with the
  // empty world
  useEventSubscription('worldErased', () => {
    setLivePartyMonsters([]);
    setLiveFollowingMonsters([]);
    setPlayerMonster(null);
    followingHook.getFollowingMonsters();
    partyHook.getActiveParty();
    loadPlayer();
  });

  useEventSubscription('monsterUpdated', ({ monster }) => {
    if (!monster?.id) return;
    patchRosterLists((existing) => (existing.id === monster.id ? monster : existing));
  });

  useEventSubscription('monsterAbilityAdded', ({ monsterId, ability }) => {
    if (!monsterId || !ability) return;
    patchRosterLists((monster) =>
      monster.id === monsterId
        ? {
            ...monster,
            abilities: [...(monster.abilities || []), ability],
            abilityCount: (monster.abilityCount || 0) + 1,
          }
        : monster,
    );
  });

  useEventSubscription('monsterArtReady', ({ monsterId, imagePath }) => {
    if (!monsterId || !imagePath) return;
    patchRosterLists((monster) =>
      monster.id === monsterId
        ? { ...monster, cardArt: { exists: true, relativePath: imagePath } }
        : monster,
    );
  });

  // Helper functions for party management
  const isInParty = (monsterId) => {
    return partyHook.ids.includes(monsterId);
  };

  const isPlayerMonster = (monsterId) => {
    return !!playerMonster && playerMonster.id === monsterId;
  };

  // Combatants stay capped at MAX_PARTY_SIZE: the player character
  // takes one slot, leaving one fewer for companions (mirrors
  // backend/game/state/manager.companion_cap)
  const companionCap = playerMonster ? GAME_RULES.MAX_PARTY_SIZE - 1 : GAME_RULES.MAX_PARTY_SIZE;

  const isPartyFull = () => {
    return partyHook.count >= companionCap;
  };

  const canAddToParty = (monsterId) => {
    return !isInParty(monsterId) && !isPartyFull();
  };

  // Add monster to party
  const addToParty = async (monster) => {
    // Don't add if already in party or party is full
    if (isInParty(monster.id) || isPartyFull()) {
      console.warn('Cannot add monster to party:', {
        alreadyInParty: isInParty(monster.id),
        partyFull: isPartyFull(),
      });
      return;
    }

    try {
      // Add to active party
      const newPartyIds = [...partyHook.ids, monster.id];
      await setPartyHook.setActiveParty(newPartyIds);

      // Refresh party data after backend confirms
      await partyHook.getActiveParty();

      console.log('✅ Added monster to party:', monster.id);
    } catch (error) {
      console.error('Failed to add monster to party:', error);
    }
  };

  // Remove monster from party
  const removeFromParty = async (monsterId) => {
    if (!isInParty(monsterId)) {
      console.warn('Monster not in party:', monsterId);
      return;
    }

    try {
      // Remove from active party
      const newPartyIds = partyHook.ids.filter((id) => id !== monsterId);
      await setPartyHook.setActiveParty(newPartyIds);

      // Refresh party data after backend confirms
      await partyHook.getActiveParty();

      console.log('✅ Removed monster from party:', monsterId);
    } catch (error) {
      console.error('Failed to remove monster from party:', error);
    }
  };

  // Toggle monster in/out of party
  const toggleParty = async (monster) => {
    if (isInParty(monster.id)) {
      await removeFromParty(monster.id);
    } else {
      await addToParty(monster);
    }
  };

  // Clear entire party
  const clearParty = async () => {
    try {
      await setPartyHook.setActiveParty([]);
      await partyHook.getActiveParty();

      console.log('✅ Cleared party');
    } catch (error) {
      console.error('Failed to clear party:', error);
    }
  };

  const isFollowing = (monsterId) => {
    return followingHook.ids.includes(monsterId);
  };

  // Combined loading state - loading if any write operation is happening OR fetching monsters
  const isLoading = setPartyHook.isLoading || partyHook.isLoading;
  const loadingFollowers = followingHook.isLoading;

  // The value object that gets put in the magical box
  const value = {
    // State - use hook data
    party: partyHook.ids,
    partyMonsters: livePartyMonsters, // Full monster objects, live-patched by growth events
    isLoading,

    followingMonsters: liveFollowingMonsters, // Full monster objects, live-patched like the party
    followingSize: followingHook.count,
    loadingFollowers,

    // The player character (null on pre-character worlds)
    playerMonster,
    companionCap,

    // Computed values - use hook data
    partySize: partyHook.count,
    isPartyFull: isPartyFull(),
    isPartyEmpty: partyHook.count === 0,

    // Helper functions
    isInParty,
    isFollowing,
    isPlayerMonster,
    canAddToParty,

    // Actions
    addToParty,
    removeFromParty,
    toggleParty,
    clearParty,
  };

  return <PartyContext.Provider value={value}>{children}</PartyContext.Provider>;
}

export default PartyProvider;
