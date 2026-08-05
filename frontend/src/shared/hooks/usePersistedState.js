// usePersistedState - useState that survives page reloads via localStorage
// WHY: the dev overlay panels must start collapsed so a new player's first
// sight is the game, not debug tooling - but a developer who opens them
// wants them to stay open across refreshes.

import { useState, useEffect } from 'react';

export function usePersistedState(storageKey, defaultValue) {
  const [value, setValue] = useState(() => {
    try {
      const stored = window.localStorage.getItem(storageKey);
      return stored === null ? defaultValue : JSON.parse(stored);
    } catch {
      // Blocked storage or corrupt value - fall back to the default
      return defaultValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(value));
    } catch {
      // Storage unavailable - session-only state is fine for a dev tool
    }
  }, [storageKey, value]);

  return [value, setValue];
}
