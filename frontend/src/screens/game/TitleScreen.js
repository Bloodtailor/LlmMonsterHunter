// TitleScreen.js - The game's opening screen
// New Game starts the guided first run (it wipes nothing - the opening
// simply plays against the existing world). Continue appears once the
// guided opening has ever been finished and goes straight to home base.

import React, { useEffect } from 'react';
import { Button, Card, CardSection, LoadingContainer } from '../../shared/ui/index.js';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as gameStateApi from '../../api/services/gameState.js';

function TitleScreen() {
  const { navigateToGameScreen } = useNavigation();

  // ✨ Automatically uses getGameState.defaults
  const api = useAsyncState(gameStateApi.getGameState);
  const { execute: loadGameState } = api;

  useEffect(() => {
    loadGameState();
  }, [loadGameState]);

  const firstRunComplete = !!api.data.firstRunComplete;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        maxWidth: '720px',
        margin: '48px auto 0',
      }}
    >
      <Card size="xl" background="dark">
        <CardSection type="header" size="xl" title="🐲 LLM Monster Hunter" alignment="center">
          <p style={{ fontStyle: 'italic', color: 'var(--color-text-secondary)' }}>
            Somewhere in the deep places sleeps a power that grants any wish — and everything down
            there wants it as badly as you do.
          </p>
        </CardSection>
      </Card>

      <Card size="xl" background="light">
        <CardSection type="content" alignment="center" padding="lg">
          {api.isLoading ? (
            <LoadingContainer isLoading={true} loadingText="Reading the world's story so far..." />
          ) : (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                alignItems: 'center',
              }}
            >
              <Button
                size="xl"
                icon="✨"
                variant="primary"
                onClick={() => navigateToGameScreen('first-run-opening')}
              >
                New Game
              </Button>
              {firstRunComplete && (
                <Button
                  size="xl"
                  icon="🏠"
                  variant="secondary"
                  onClick={() => navigateToGameScreen('homebase')}
                >
                  Continue
                </Button>
              )}
            </div>
          )}
        </CardSection>
      </Card>
    </div>
  );
}

export default TitleScreen;
