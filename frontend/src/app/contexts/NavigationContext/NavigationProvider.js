// NavigationProvider.js - Provides game navigation state to the app
// Simple clean version following the EventProvider pattern
// Manages only game screen navigation, not top-level app navigation

import React, { useState } from 'react';
import { NavigationContext } from './NavigationContext.js';

/**
 * NavigationProvider component
 * Provides game screen navigation state and actions to child components
 * @param {object} props - Provider props
 * @param {React.ReactNode} props.children - Child components
 */
function NavigationProvider({ children }) {
  
  // Game screen navigation state - starts at homebase
  const [currentGameScreen, setCurrentGameScreen] = useState('homebase');

  /**
   * Navigate to a different game screen
   * @param {string} screen - Game screen identifier
   */
  const navigateToGameScreen = (screen) => {
    setCurrentGameScreen(screen);
  };

  // Create context value
  const contextValue = {
    currentGameScreen,
    navigateToGameScreen
  };

  return (
    <NavigationContext.Provider value={contextValue}>
      {children}
    </NavigationContext.Provider>
  );
}

export default NavigationProvider;