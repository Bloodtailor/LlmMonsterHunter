// BattleOutcomeView.js - Victory or defeat
// Victory: continue exploring from this location
// Defeat: the run is over - return to home base

import React from 'react';
import { Card, CardSection, Button } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

function BattleOutcomeView() {
  const { outcome, outcomeText, joinedNames, isProcessing, resetBattle } = useBattleContext();
  const { continueExploring, resetDungeon } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

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
