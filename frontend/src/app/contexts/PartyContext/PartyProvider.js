// PartyProvider.js - The component that puts data IN the magical box
// This manages party state and provides functions to modify it
// UPDATED: Now fetches individual monster data for party members using useMonster hook

import React, { useEffect, useState, useMemo } from 'react';
import { PartyContext } from './PartyContext.js';
import { GAME_RULES } from '../../../shared/constants/constants.js';
import {
  useFollowingMonsters,
  useActiveParty,
  useSetActiveParty
} from '../../hooks/useGameState.js';
import { useEventSubscription } from '../../../api/events/useEventSubscription.js';

function PartyProvider({ children }) {
  // Domain hooks for game state
  const followingHook  = useFollowingMonsters();
  const partyHook = useActiveParty();
  const setPartyHook = useSetActiveParty();

  // Load initial data
  useEffect(() => {
    followingHook.getFollowingMonsters();
    partyHook.getActiveParty();
  }, [followingHook.getFollowingMonsters, partyHook.getActiveParty]);

  // Live copy of the party's monsters - growth moments (stat bumps, new
  // or reworded abilities, persona notes) patch cards in place, so camp
  // and exit ceremonies show on the party panel without a refetch
  const [livePartyMonsters, setLivePartyMonsters] = useState(partyHook.partyMonsters);

  useEffect(() => {
    setLivePartyMonsters(partyHook.partyMonsters);
  }, [partyHook.partyMonsters]);

  useEventSubscription('monsterUpdated', ({ monster }) => {
    if (!monster?.id) return;
    setLivePartyMonsters(prev => (prev || []).map(existing =>
      existing.id === monster.id ? monster : existing
    ));
  });

  useEventSubscription('monsterAbilityAdded', ({ monsterId, ability }) => {
    if (!monsterId || !ability) return;
    setLivePartyMonsters(prev => (prev || []).map(monster =>
      monster.id === monsterId
        ? { ...monster, abilities: [...(monster.abilities || []), ability], abilityCount: (monster.abilityCount || 0) + 1 }
        : monster
    ));
  });

  // Helper functions for party management
  const isInParty = (monsterId) => {
    return partyHook.ids.includes(monsterId);
  };

  const isPartyFull = () => {
    return partyHook.count >= GAME_RULES.MAX_PARTY_SIZE;
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
        partyFull: isPartyFull() 
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
      const newPartyIds = partyHook.ids.filter(id => id !== monsterId);
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

    followingMonsters: followingHook.followingMonsters,
    followingSize: followingHook.count,
    loadingFollowers,
    
    
    // Computed values - use hook data
    partySize: partyHook.count,
    isPartyFull: isPartyFull(),
    isPartyEmpty: partyHook.count === 0,
    
    // Helper functions
    isInParty,
    isFollowing,
    canAddToParty,
    
    // Actions
    addToParty,
    removeFromParty,
    toggleParty,
    clearParty
  };

  return (
    <PartyContext.Provider value={value}>
      {children}
    </PartyContext.Provider>
  );
}

export default PartyProvider;