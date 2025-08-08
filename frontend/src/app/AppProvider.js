// AppProvider.js - Main application provider that orchestrates all context initialization
// Shows loading spinner only on first page load, then never again during browser session
// Waits for all contexts to be ready before rendering app content

import React, { useState, useEffect } from 'react';
import { EventProvider, useEventContext } from './contexts/EventContext';
import { PartyProvider, useParty } from './contexts/PartyContext';
import AppLoadingScreen from '../screens/game/AppLoadingScreen';

// Session storage key for tracking initialization
const SESSION_KEY = 'app_initialized';

/**
 * Inner component that can access both contexts to check readiness
 * This must be inside both providers to access their context values
 */
function AppInitializer({ children }) {
  const [isFirstLoad, setIsFirstLoad] = useState(false);
  const [showLoadingScreen, setShowLoadingScreen] = useState(false);

  // Access context states to determine readiness
  const eventContext = useEventContext();
  const partyContext = useParty();

  // Check if contexts are ready
  const isEventProviderReady = eventContext.isConnected && !eventContext.connectionError;
  const isPartyProviderReady = !partyContext.isLoading  && !partyContext.loadingFollowers;
  
  const allContextsReady = isEventProviderReady && isPartyProviderReady;

  // Check if this is first load of the session
  useEffect(() => {
    const hasInitialized = sessionStorage.getItem(SESSION_KEY);
    const isFirstTime = !hasInitialized;
    
    setIsFirstLoad(isFirstTime);
    setShowLoadingScreen(isFirstTime);

    if (isFirstTime) {
      console.log('🚀 First app load - showing initialization screen');
    } else {
      console.log('✅ App previously initialized this session - skipping loading screen');
    }
  }, []);

  // Handle context readiness
  useEffect(() => {
    if (allContextsReady && isFirstLoad) {
      console.log('✅ All contexts ready - hiding loading screen');
      
      // Mark app as initialized in session storage
      sessionStorage.setItem(SESSION_KEY, 'true');
      
      // Hide loading screen after brief delay to avoid flash
      setTimeout(() => {
        setShowLoadingScreen(false);
      }, 300);
    }
  }, [allContextsReady, isFirstLoad]);

  // Show loading screen during first load initialization
  if (showLoadingScreen) {
    return (
      <AppLoadingScreen
        loadingStates={[
          { isLoading: true, message: "Connecting to server..." },
          { isLoading: false, message: "Creating SSE connections..." },
          { isLoading: false, message: "Loading party states..." }
        ]}
        errorStates={[
          { hasError: false, message: "Could not connect to server"  },
          { hasError: false, message: "Error subscribing to SSE events", error: "eventError this is a very long message that spanse multile lines and I can barely type. idk what happened to my ability to type really fast but I have slowed down a whole lot. It is really hard for me to do the punctuation as fast as I do the other things, so I end up stopping? what about now! Hahaha! this is great!!! we love to see it? Now is the time for BATTLE!!!" },
          { hasError: false, message: "Error fetching party state", error: "partyError" }
        ]}
        title="🎮 Monster Hunter Game"
        successMessage="The game is ready!"
        />
    );
  }

  // Render app content (contexts are ready or this isn't first load)
  return children;
}

/**
 * Main AppProvider that wraps all contexts and handles initialization
 * This is what App.js should use instead of manually wrapping providers
 */
function AppProvider({ children }) {
  return (
    <EventProvider>
      <PartyProvider>
        <AppInitializer>
          {children}
        </AppInitializer>
      </PartyProvider>
    </EventProvider>
  );
}

export default AppProvider;