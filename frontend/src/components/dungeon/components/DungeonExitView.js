// DungeonExitView.js - The party takes an exit path and leaves the dungeon
// PERFORMANCE FOCUSED - Only consumes exitText
// Shows the exit narrative and returns the party to home base

import React from 'react';
import { Card, CardSection, Button } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * DungeonExitView component
 * Exit narrative + return home - the dungeon run is over
 */
function DungeonExitView() {
  const { exitText, resetDungeon } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  if (!exitText) return null;

  const handleReturnHome = () => {
    resetDungeon();
    navigateToGameScreen('homebase');
  };

  const textStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    padding: '24px',
    whiteSpace: 'pre-wrap',
    fontFamily: 'var(--font-family-serif)'
  };

  return (
    <>
      <Card size="xl" background="light">
        <CardSection type="header" size="xl" title="🌅 Back to the Surface" alignment="center" />
      </Card>

      <Card size="xl" background="dark">
        <CardSection type="content" padding="none">
          <div style={textStyles}>
            {exitText}
          </div>
        </CardSection>
      </Card>

      <Card size="xl" background="light">
        <CardSection type="content" alignment="center">
          <Button
            size="xl"
            icon="🏠"
            variant="primary"
            onClick={handleReturnHome}
          >
            Return to Home Base
          </Button>
        </CardSection>
      </Card>
    </>
  );
}

export default DungeonExitView;
