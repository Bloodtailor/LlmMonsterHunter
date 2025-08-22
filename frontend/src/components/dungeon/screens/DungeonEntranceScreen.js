// DungeonEntranceScreen.js - Dungeon entrance with streaming event text
// CLEAN VERSION - Uses DungeonContext for simple, business-focused state
// Just shows streaming text and enables continue when doors are ready

import React, { useEffect, useRef } from 'react';
import { Card, CardSection, Button, Alert } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

/**
 * DungeonEntranceScreen component
 * Shows streaming dungeon entry text using clean DungeonContext
 * Simple business logic: show text, enable continue when ready
 */
function DungeonEntranceScreen() {
  const { navigateToGameScreen } = useNavigation();
  
  // Ref to track if we've already called enterDungeon
  const hasEnteredRef = useRef(false);
  
  // Clean business-focused state from DungeonContext
  const {
    entryText,        // Streaming entry text
    isDoorsReady,     // Enable continue button when true
    isError,          // Show error UI when true
    error,            // Error message to display
    enterDungeon,     // Start the workflow
    resetDungeon      // Clear state and go back
  } = useDungeon();

  // Auto-enter dungeon when component mounts (only once)
  useEffect(() => {
    if (!hasEnteredRef.current) {
      console.log('DungeonEntranceScreen: Auto-entering dungeon');
      hasEnteredRef.current = true;
      enterDungeon();
    }
  }, [enterDungeon]);

  // Handle continue to doors
  const handleContinue = () => {
    navigateToGameScreen('dungeon-doors');
  };

  // Handle back to home base
  const handleBackToHome = () => {
    hasEnteredRef.current = false; // Reset ref so we can enter again later
    resetDungeon(); // Clear dungeon state
    navigateToGameScreen('homebase');
  };

  // Render error state
  if (isError) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <Card size="xl" background="light">
          <CardSection type="header" size="xl" title="🏰 Dungeon Entrance" alignment="center" />
          <CardSection type="content" alignment="center">
            <Alert type="error" title="Dungeon Entry Failed">
              {error || 'Something went wrong while entering the dungeon.'}
            </Alert>
            <div style={{ marginTop: '24px' }}>
              <Button onClick={handleBackToHome} size="lg" variant="secondary">
                ← Back to Home Base
              </Button>
            </div>
          </CardSection>
        </Card>
      </div>
    );
  }

  // Main screen with streaming text
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <Card size="xl" background="light">
        <CardSection type="header" size="xl" title="🏰 Dungeon Entrance" alignment="center">
          <p>The dungeon portal shimmers before you...</p>
        </CardSection>
      </Card>

      {/* Streaming Entry Text */}
      <Card size="xl" background="default">
        <CardSection type="content" size="lg">
          <div style={{
            minHeight: '200px',
            padding: '24px',
            backgroundColor: 'var(--color-surface-secondary)',
            borderRadius: 'var(--radius-md)',
            border: '2px solid var(--color-border-primary)',
            position: 'relative'
          }}>
            {/* Streaming text display */}
            <div style={{
              fontSize: 'var(--font-size-lg)',
              lineHeight: 'var(--line-height-relaxed)',
              color: 'var(--color-text-primary)',
              whiteSpace: 'pre-wrap'
            }}>
              {entryText || 'Preparing your dungeon entry...'}
            </div>

            {/* Streaming indicator - show when we have text but doors aren't ready */}
            {entryText && !isDoorsReady && (
              <div style={{
                position: 'absolute',
                bottom: '12px',
                right: '12px',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-muted)',
                fontStyle: 'italic'
              }}>
                Generating doors...
              </div>
            )}
          </div>
        </CardSection>
      </Card>

      {/* Action Buttons */}
      <Card size="xl" background="light">
        <CardSection type="content" alignment="center">
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Button 
              onClick={handleBackToHome}
              size="lg" 
              variant="secondary"
            >
              ← Back to Home Base
            </Button>

            <Button 
              onClick={handleContinue}
              size="lg" 
              disabled={!isDoorsReady}
              icon={isDoorsReady ? "🚪" : null}
            >
              {isDoorsReady ? "Continue to Doors" : "Preparing Doors..."}
            </Button>
          </div>

          {/* Status indicator */}
          <div style={{ 
            marginTop: '16px', 
            fontSize: 'var(--font-size-sm)', 
            color: 'var(--color-text-muted)',
            textAlign: 'center'
          }}>
            {!entryText && 'Starting dungeon entry...'}
            {entryText && !isDoorsReady && 'Generating dungeon doors...'}
            {isDoorsReady && 'Ready to explore!'}
          </div>
        </CardSection>
      </Card>

      {/* Simple Debug Info (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <Card size="md" background="default">
          <CardSection type="header" title="Debug Info" />
          <CardSection type="content">
            <div style={{ fontSize: 'var(--font-size-sm)', fontFamily: 'monospace' }}>
              <div>Entry Text Length: {entryText.length} chars</div>
              <div>Doors Ready: {isDoorsReady ? 'Yes' : 'No'}</div>
              <div>Is Error: {isError ? 'Yes' : 'No'}</div>
              <div>Error: {error || 'None'}</div>
            </div>
          </CardSection>
        </Card>
      )}
    </div>
  );
}

export default DungeonEntranceScreen;