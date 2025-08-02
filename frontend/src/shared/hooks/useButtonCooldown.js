// useButtonCooldown.js - Simple spam protection for buttons
// Prevents rapid clicking with configurable cooldown period

import { useState, useCallback } from 'react';

/**
 * Hook for button spam protection with cooldown
 * @param {number} cooldownMs - Cooldown period in milliseconds (default: 3000)
 * @returns {object} Hook result with trigger function and cooldown state
 */
export function useCooldown(cooldownMs = 3000) {
  const [isOnCooldown, setIsOnCooldown] = useState(false);

  /**
   * Start the cooldown period
   */
  const startCooldown = useCallback(() => {
    if (isOnCooldown) return false; // Already on cooldown
    
    setIsOnCooldown(true);
    setTimeout(() => {
      setIsOnCooldown(false);
    }, cooldownMs);
    
    return true; // Cooldown started
  }, [isOnCooldown, cooldownMs]);

  return {
    startCooldown,
    isOnCooldown
  };
}

export default useCooldown;