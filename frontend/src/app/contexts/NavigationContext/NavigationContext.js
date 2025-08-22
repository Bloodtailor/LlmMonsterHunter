// NavigationContext.js - Context for game screen navigation
// Manages navigation state between game screens only
// Follows established context pattern from PartyContext and EventContext

import { createContext } from 'react';

/**
 * Navigation context for game screen management
 * Provides currentGameScreen state and navigation functions
 * Only handles navigation within the game - App.js handles top-level navigation
 */
export const NavigationContext = createContext(null);