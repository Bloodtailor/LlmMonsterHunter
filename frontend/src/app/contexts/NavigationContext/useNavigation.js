// useNavigation.js - Hook to access game navigation from any component
// Consumer hook for NavigationContext following the useParty/useEventContext pattern
// Only handles game screen navigation

import { useContext } from 'react';
import { NavigationContext } from './NavigationContext.js';

/**
 * Hook to access game navigation state and actions
 * Must be used within a NavigationProvider (typically within game screens)
 * 
 * @returns {object} Navigation state and functions
 */
export function useNavigation() {
  const context = useContext(NavigationContext);
  
  if (context === null) {
    throw new Error(
      'useNavigation must be used within a NavigationProvider. ' +
      'Make sure your component is wrapped with <NavigationProvider>.'
    );
  }
  
  return context;
}