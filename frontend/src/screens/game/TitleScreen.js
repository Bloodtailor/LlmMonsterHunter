// TitleScreen.js - The game's opening screen
// New Game is a promise: it ERASES the world (POST /api/game-state/new-game)
// behind an explicit confirmation step whenever anything meaningful
// exists to lose. Continue appears whenever a world exists to return
// to; a run the last session never finished is swept first - struck
// down by an unknown force - so the player wakes at the home base.

import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, CardSection, LoadingContainer } from '../../shared/ui/index.js';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as gameStateApi from '../../api/services/gameState.js';
import { abandonRun } from '../../api/services/dungeon.js';

function TitleScreen() {
  const { navigateToGameScreen } = useNavigation();

  // ✨ Automatically uses getGameState.defaults
  const api = useAsyncState(gameStateApi.getGameState);
  const { execute: loadGameState } = api;

  // The destructive-confirm step: the erase only happens after the
  // player has read what New Game means (skipped for an empty world)
  const [confirmingErase, setConfirmingErase] = useState(false);
  const [isErasing, setIsErasing] = useState(false);
  const [eraseError, setEraseError] = useState(null);

  // The interrupted-run step: Continue with a live run on record first
  // tells the story of how it ended, then sweeps it and heads home
  const [showInterruption, setShowInterruption] = useState(false);
  const [isWaking, setIsWaking] = useState(false);
  const [continueError, setContinueError] = useState(null);

  useEffect(() => {
    loadGameState();
  }, [loadGameState]);

  const hasWorldData = !!api.data.hasWorldData;
  const inDungeon = !!api.data.inDungeon;

  const eraseAndBegin = async () => {
    setIsErasing(true);
    setEraseError(null);
    try {
      const result = await gameStateApi.startNewGame();
      if (!result.success) {
        setEraseError(result.error || 'The world would not let go - try again.');
        setIsErasing(false);
        return;
      }
      navigateToGameScreen('character-creation');
    } catch (error) {
      setEraseError(error.message || 'The world would not let go - try again.');
      setIsErasing(false);
    }
  };

  const handleNewGame = () => {
    if (hasWorldData) {
      setConfirmingErase(true);
    } else {
      eraseAndBegin();
    }
  };

  const handleContinue = () => {
    if (inDungeon) {
      // A run is still on record from a session that never finished -
      // tell the player how it ended before sweeping it
      setShowInterruption(true);
      return;
    }
    navigateToGameScreen('homebase');
  };

  const wakeAtHome = async () => {
    setIsWaking(true);
    setContinueError(null);
    try {
      await abandonRun({ interrupted: true });
      navigateToGameScreen('homebase');
    } catch (error) {
      setContinueError(error.message || 'The way home is blocked - try again.');
      setIsWaking(false);
    }
  };

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

      {eraseError && (
        <Alert type="error" title="The new game could not begin">
          {String(eraseError)}
        </Alert>
      )}

      {continueError && (
        <Alert type="error" title="Could not continue">
          {String(continueError)}
        </Alert>
      )}

      <Card size="xl" background="light">
        <CardSection type="content" alignment="center" padding="lg">
          {api.isLoading ? (
            <LoadingContainer isLoading={true} loadingText="Reading the world's story so far..." />
          ) : confirmingErase ? (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                alignItems: 'center',
              }}
            >
              <p style={{ fontWeight: 'var(--font-weight-bold)', margin: 0 }}>
                Begin a completely new story?
              </p>
              <p
                style={{
                  color: 'var(--color-text-secondary)',
                  textAlign: 'center',
                  margin: 0,
                }}
              >
                Every monster, memory, conversation, evolution, and chronicle in this world will be
                erased forever. This cannot be undone.
              </p>
              <Button
                size="xl"
                icon="🔥"
                variant="danger"
                disabled={isErasing}
                onClick={eraseAndBegin}
              >
                {isErasing ? 'The old world fades...' : 'Erase everything and begin'}
              </Button>
              <Button
                size="lg"
                variant="secondary"
                disabled={isErasing}
                onClick={() => setConfirmingErase(false)}
              >
                Keep my world
              </Button>
            </div>
          ) : showInterruption ? (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                alignItems: 'center',
              }}
            >
              <p style={{ fontWeight: 'var(--font-weight-bold)', margin: 0 }}>
                The last expedition never came home
              </p>
              <p
                style={{
                  color: 'var(--color-text-secondary)',
                  textAlign: 'center',
                  margin: 0,
                }}
              >
                An unknown force overwhelmed the party mid-journey — whatever that run had gathered
                was lost to the dark. They wake safe at the home base, and the story carries the
                scar.
              </p>
              <Button
                size="xl"
                icon="🏠"
                variant="primary"
                disabled={isWaking}
                onClick={wakeAtHome}
              >
                {isWaking ? 'Waking...' : 'Wake at the home base'}
              </Button>
            </div>
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
                disabled={isErasing}
                onClick={handleNewGame}
              >
                {isErasing ? 'The story gathers itself...' : 'New Game'}
              </Button>
              {hasWorldData && (
                <Button
                  size="xl"
                  icon="🏠"
                  variant="secondary"
                  disabled={isErasing}
                  onClick={handleContinue}
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
