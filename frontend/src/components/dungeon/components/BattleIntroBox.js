// BattleIntroBox.js - The hostile monsters' challenge and the call to arms
// Appears on the location screen when a battle encounter is ready
// (choose_path completed with monster_battle)

import React from 'react';
import { Card, CardSection, Button } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

function BattleIntroBox() {
  const { battleIntro, displayedBattle, beginBattle } = useBattleContext();
  const { exitText } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  if (exitText || !battleIntro || !displayedBattle?.in_battle) return null;

  const handleBeginBattle = () => {
    beginBattle();  // opening initiative - the LLM decides who moves first
    navigateToGameScreen('dungeon-battle');
  };

  const speechStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-family-serif)',
    fontStyle: 'italic',
    whiteSpace: 'pre-wrap'
  };

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="lg" title="⚔️ The monsters confront you!" alignment="center" />

      <CardSection type="content" alignment="center">
        <p style={speechStyles}>"{battleIntro}"</p>
      </CardSection>

      <CardSection type="content" alignment="center">
        <Button
          size="xl"
          icon="⚔️"
          variant="primary"
          onClick={handleBeginBattle}
        >
          Begin Battle
        </Button>
      </CardSection>
    </Card>
  );
}

export default BattleIntroBox;
