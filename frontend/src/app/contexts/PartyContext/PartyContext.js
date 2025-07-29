// PartyContext.js - The "magical box" for party data
// This creates the context that components can access from anywhere

import { createContext } from 'react';

// Create the context (the "magical box")
// This is just the container - it doesn't have any data yet
export const PartyContext = createContext(null);

// We'll build the Provider and hook in separate files to keep things organized
// This pattern makes it easy to find and modify party logic later