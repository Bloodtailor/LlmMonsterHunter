// Party Manager Component
// Handles adding/removing monsters from active party
// Provides party management functions and state management

import { useState } from 'react';
import { setActiveParty, isPartyReady } from '../../services/gameStateApi';

/**
 * Custom hook for party management
 * @param {Function} onPartyChange - Callback when party changes
 * @returns {Object} Party management functions and state
 */
export function usePartyManager(onPartyChange) {
  const [updating, setUpdating] = useState(false);

  /**
   * Add monster to active party
   * @param {Object} monster - Monster to add to party
   * @param {Array} currentParty - Current party monsters
   * @returns {Promise<boolean>} Success status
   */
  const addToParty = async (monster, currentParty) => {
    // Check party size limit
    if (currentParty.length >= 4) {
      alert('Party is full! Remove a monster before adding a new one.');
      return false;
    }

    // Check if monster is already in party
    if (currentParty.find(m => m.id === monster.id)) {
      console.log('Monster is already in party:', monster.name);
      return false;
    }

    setUpdating(true);
    try {
      // Create new party with added monster
      const newPartyIds = [...currentParty.map(m => m.id), monster.id];
      
      const response = await setActiveParty(newPartyIds);
      
      if (response.success) {
        console.log(`✅ Added ${monster.name} to party`);
        
        // Check if party is now ready
        const readyResponse = await isPartyReady();
        
        // Notify parent component
        if (onPartyChange) {
          onPartyChange({
            party: response.active_party?.details || [],
            ready: readyResponse.ready_for_dungeon || false
          });
        }
        
        return true;
      } else {
        console.error('Failed to add monster to party:', response.error);
        alert(`Failed to add ${monster.name} to party: ${response.error}`);
        return false;
      }
    } catch (error) {
      console.error('Error adding monster to party:', error);
      alert(`Error adding ${monster.name} to party`);
      return false;
    } finally {
      setUpdating(false);
    }
  };

  /**
   * Remove monster from active party
   * @param {Object} monster - Monster to remove from party
   * @param {Array} currentParty - Current party monsters
   * @returns {Promise<boolean>} Success status
   */
  const removeFromParty = async (monster, currentParty) => {
    // Check if monster is in party
    if (!currentParty.find(m => m.id === monster.id)) {
      console.log('Monster is not in party:', monster.name);
      return false;
    }

    setUpdating(true);
    try {
      // Create new party without removed monster
      const newPartyIds = currentParty
        .filter(m => m.id !== monster.id)
        .map(m => m.id);
      
      const response = await setActiveParty(newPartyIds);
      
      if (response.success) {
        console.log(`✅ Removed ${monster.name} from party`);
        
        // Check if party is still ready
        const readyResponse = await isPartyReady();
        
        // Notify parent component
        if (onPartyChange) {
          onPartyChange({
            party: response.active_party?.details || [],
            ready: readyResponse.ready_for_dungeon || false
          });
        }
        
        return true;
      } else {
        console.error('Failed to remove monster from party:', response.error);
        alert(`Failed to remove ${monster.name} from party: ${response.error}`);
        return false;
      }
    } catch (error) {
      console.error('Error removing monster from party:', error);
      alert(`Error removing ${monster.name} from party`);
      return false;
    } finally {
      setUpdating(false);
    }
  };

  return {
    addToParty,
    removeFromParty,
    updating
  };
}

/**
 * Party Toggle Button Component
 * Small button that appears on monster cards for party management
 * @param {Object} props - Component props
 * @param {Object} props.monster - Monster object
 * @param {boolean} props.isInParty - Whether monster is in active party
 * @param {boolean} props.isPartyFull - Whether party has 4 monsters
 * @param {Function} props.onToggle - Callback for toggle action
 * @param {boolean} props.disabled - Whether button is disabled
 */
export function PartyToggleButton({ monster, isInParty, isPartyFull, onToggle, disabled }) {
  const handleClick = (e) => {
    // Prevent event from bubbling to card (which would trigger flip)
    e.stopPropagation();
    
    if (disabled) return;
    
    if (onToggle) {
      onToggle(monster, isInParty);
    }
  };

  // Determine button state and appearance
  const getButtonState = () => {
    if (disabled) {
      return {
        icon: '⏳',
        className: 'party-toggle-disabled',
        title: 'Updating party...'
      };
    }
    
    if (isInParty) {
      return {
        icon: '✓',
        className: 'party-toggle-remove',
        title: `Remove ${monster.name} from party`
      };
    }
    
    if (isPartyFull) {
      return {
        icon: '🚫',
        className: 'party-toggle-full',
        title: 'Party is full (4/4)'
      };
    }
    
    return {
      icon: '+',
      className: 'party-toggle-add',
      title: `Add ${monster.name} to party`
    };
  };

  const buttonState = getButtonState();

  return (
    <button
      className={`party-toggle-button ${buttonState.className}`}
      onClick={handleClick}
      disabled={disabled || (isPartyFull && !isInParty)}
      title={buttonState.title}
    >
      {buttonState.icon}
    </button>
  );
}