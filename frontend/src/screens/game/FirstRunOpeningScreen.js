// FirstRunOpeningScreen.js - New Game's guided opening
// Streams the opening scene (the wish-granting premise), then enters the
// guided first dungeon from RIGHT HERE - the entrance notice board is a
// normal-run flow and never appears on a first run. Once entry begins,
// the familiar entry text + continue button take over.

import React, { useEffect, useRef, useState } from 'react';
import { Button, Card, CardSection } from '../../shared/ui/index.js';
import { useDungeon } from '../../app/contexts/DungeonContext/index.js';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';
import * as playerApi from '../../api/services/player.js';
import DungeonEntryText from '../../components/dungeon/components/DungeonEntryText.js';
import ContinueToDoorsButton from '../../components/dungeon/components/ContinueToDoorsButton.js';
import DungeonErrorAlert from '../../components/dungeon/components/DungeonErrorAlert.js';

const openingTextStyles = {
  fontSize: 'var(--font-size-lg)',
  lineHeight: 'var(--line-height-relaxed)',
  color: 'var(--color-text-primary)',
  padding: '24px',
  minHeight: '160px',
  whiteSpace: 'pre-wrap',
  fontFamily: 'var(--font-family-serif)',
};

function FirstRunOpeningScreen() {
  const { openingText, isOpeningReady, beginFirstRun, enterFirstRun } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  // Whether the player has stepped inside (the run is underway)
  const [hasStepped, setHasStepped] = useState(false);

  // The opening plays once per visit to this screen - and only for a
  // finished character (New Game routes through creation first; landing
  // here without one is a stale navigation, sent back to the wizard)
  const hasBegunRef = useRef(false);
  useEffect(() => {
    if (hasBegunRef.current) return;
    hasBegunRef.current = true;
    playerApi.getPlayer().then(({ player }) => {
      if (player && player.generationStage === 'complete') {
        beginFirstRun();
      } else {
        navigateToGameScreen('character-creation');
      }
    });
  }, [beginFirstRun, navigateToGameScreen]);

  const stepInside = () => {
    setHasStepped(true);
    enterFirstRun();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <DungeonErrorAlert />

      <Card size="xl" background="light">
        <CardSection type="header" size="xl" title="✨ A Wish, and a Door" alignment="center" />
      </Card>

      {/* The opening scene, streamed */}
      <Card size="xl" background="dark">
        <CardSection type="content" padding="none">
          <div style={openingTextStyles}>
            {openingText || 'The story gathers its first words...'}
          </div>
        </CardSection>
      </Card>

      {!hasStepped ? (
        <Card size="xl" background="light">
          <CardSection type="content" alignment="center" padding="sm">
            <Button
              size="xl"
              icon="🏰"
              variant={isOpeningReady ? 'primary' : 'secondary'}
              disabled={!isOpeningReady}
              onClick={stepInside}
            >
              {isOpeningReady ? 'Take the First Step' : 'The story is being written...'}
            </Button>
          </CardSection>
        </Card>
      ) : (
        <>
          {/* The run is underway - entry text streams, then the paths */}
          <Card size="xl" background="dark">
            <CardSection type="content" padding="none">
              <DungeonEntryText />
            </CardSection>
          </Card>
          <Card size="xl" background="light">
            <CardSection type="content" alignment="center" padding="sm">
              <ContinueToDoorsButton />
            </CardSection>
          </Card>
        </>
      )}
    </div>
  );
}

export default FirstRunOpeningScreen;
