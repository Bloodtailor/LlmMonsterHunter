// AppProvider.js - Main application provider that orchestrates all context initialization
// Shows loading spinner only on first page load, then never again during browser session
// Waits for all contexts to be ready before rendering app content

import React, { useState, useEffect } from 'react';
import { EventProvider, useEventContext } from './contexts/EventContext';
import { PartyProvider, useParty } from './contexts/PartyContext';
import { LoadingSpinner } from '../shared/ui';

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
      <div className="app-initializing">
        <div className="app-loading-container">
          <LoadingSpinner size="screen" />
          <h2>Loading Monster Hunter Game...</h2>
          <div className="loading-status">
            <div className="status-item">
              <span className={isEventProviderReady ? 'ready' : 'loading'}>
                🔗 {isEventProviderReady ? 'Events Connected' : 'Connecting to Events...'}
              </span>
            </div>
            <div className="status-item">
              <span className={isPartyProviderReady ? 'ready' : 'loading'}>
                🎮 {isPartyProviderReady ? 'Game State Loaded' : 'Loading Game State...'}
              </span>
            </div>
          </div>
        </div>

        <style jsx>{`
          .app-initializing {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
          }

          .app-loading-container {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
          }

          .app-loading-container h2 {
            color: #ffffff;
            margin: 1.5rem 0;
            font-size: 1.5rem;
            font-weight: 600;
          }

          .loading-status {
            margin-top: 2rem;
          }

          .status-item {
            margin: 0.75rem 0;
          }

          .status-item .ready {
            color: #4ade80;
            font-weight: 500;
          }

          .status-item .loading {
            color: #fbbf24;
            font-weight: 400;
          }
        `}</style>
      </div>
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