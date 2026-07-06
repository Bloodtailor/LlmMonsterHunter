// BattleOutcomeView.js - Victory or defeat
// Victory: the CoCaTok pickup ceremony (spin, explode, collected forever),
// then continue exploring from this location
// Defeat: the run is over - return to home base

import React, { useState } from 'react';
import { Card, CardSection, Button } from '../../../shared/ui/index.js';
import CoCaTok from '../../../shared/ui/CoCaTok/CoCaTok.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

function BattleOutcomeView() {
  const { outcome, outcomeText, joinedNames, victoryCocatok, isProcessing, resetBattle } = useBattleContext();
  const { continueExploring, resetDungeon } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  // The pickup ceremony: the token spins until clicked, then explodes into
  // the collection (it is already saved backend-side - this is the theater)
  const [cocatokCollected, setCocatokCollected] = useState(false);

  // Only once the player has clicked through the whole story
  if (!outcome || isProcessing) return null;

  const isVictory = outcome === 'victory';

  const handleVictoryContinue = () => {
    resetBattle();
    continueExploring();
    navigateToGameScreen('dungeon-doors');
  };

  const handleDefeatReturn = () => {
    resetBattle();
    resetDungeon();
    navigateToGameScreen('homebase');
  };

  const textStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-family-serif)',
    whiteSpace: 'pre-wrap'
  };

  return (
    <Card size="xl" background="light">
      <CardSection
        type="header"
        size="xl"
        title={isVictory ? '🏆 Victory!' : '💀 Defeat...'}
        alignment="center"
      />

      <CardSection type="content" alignment="center">
        <p style={textStyles}>{outcomeText}</p>
      </CardSection>

      {joinedNames && joinedNames.length > 0 && (
        <CardSection type="content" alignment="center">
          <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 'bold' }}>
            🎉 {joinedNames.join(' and ')} {joinedNames.length === 1 ? 'has' : 'have'} joined your followers!
          </p>
        </CardSection>
      )}

      {/* The victory's CoCaTok - click it to claim your keepsake */}
      {isVictory && victoryCocatok && (
        <CardSection type="content" alignment="center">
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
            <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 'bold', margin: 0 }}>
              {cocatokCollected
                ? `✨ "${victoryCocatok.title}" joins your collection!`
                : '✨ A CoCaTok was minted for this victory - claim it!'}
            </p>
            {!cocatokCollected && (
              <CoCaTok
                color={victoryCocatok.color}
                emoji={victoryCocatok.emoji}
                size="lg"
                onActivate={() => setCocatokCollected(true)}
              />
            )}
            <p style={{
              fontSize: 'var(--font-size-sm)',
              fontStyle: 'italic',
              fontFamily: 'var(--font-family-serif)',
              color: 'var(--color-text-secondary)',
              maxWidth: '480px',
              margin: 0
            }}>
              {victoryCocatok.commemoration}
            </p>
          </div>
        </CardSection>
      )}

      <CardSection type="content" alignment="center">
        {isVictory ? (
          <Button size="xl" icon="🧭" variant="primary" onClick={handleVictoryContinue}>
            Continue Exploring
          </Button>
        ) : (
          <Button size="xl" icon="🏠" variant="primary" onClick={handleDefeatReturn}>
            Return to Home Base
          </Button>
        )}
      </CardSection>
    </Card>
  );
}

export default BattleOutcomeView;
