// useParty.js - Hook for components to access party data
// This is what components call to get party information

import { useContext } from 'react';
import { PartyContext } from './PartyContext.js';

/**
 * Hook to access party state and actions
 * @returns {object} Party state and functions
 */
function useParty() {
  const context = useContext(PartyContext);
  
  // Make sure the hook is used inside a PartyProvider
  if (context === null) {
    throw new Error('useParty must be used within a PartyProvider');
  }
  
  return context;
}

export default useParty;