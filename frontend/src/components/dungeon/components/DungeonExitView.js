// DungeonExitView.js - The party takes an exit path and leaves the dungeon
// PERFORMANCE FOCUSED - Only consumes exitText + growthResults
// Shows the exit narrative, the exit ceremony (every member's growth
// reflection from the whole run), and returns the party to home base

import React from 'react';
import { Card, CardSection, Button, Badge } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

// Small badges for what a reflection actually changed
function growthBadges(growth) {
  const badges = [];
  if (growth.stat) badges.push(`📈 ${growth.stat} +${growth.tier}`);
  if (growth.new_ability) badges.push(`⚡ learned ${growth.new_ability}`);
  if (growth.reworded_ability) badges.push(`✍️ ${growth.reworded_ability} reworded`);
  return badges;
}

/**
 * DungeonExitView component
 * Exit narrative + the exit ceremony + return home - the run is over
 */
function DungeonExitView() {
  const { exitText, growthResults, resetDungeon } = useDungeon();
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

  const reflectionStyles = {
    fontSize: 'var(--font-size-md)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-family-serif)',
    fontStyle: 'italic',
    whiteSpace: 'pre-wrap',
    margin: 0
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

      {/* The exit ceremony - what the run made of each member */}
      {growthResults && growthResults.length > 0 && (
        <Card size="xl" background="dark">
          <CardSection type="header" size="md" title="🌱 What the Journey Made of Them" alignment="center" />
          <CardSection type="content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '720px', margin: '0 auto' }}>
              {growthResults.map((growth) => (
                <div key={growth.monster_id} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap' }}>
                    <strong>{growth.monster_name}</strong>
                    {growthBadges(growth).map((text, index) => (
                      <Badge key={index} variant="success" size="sm" pill>{text}</Badge>
                    ))}
                  </div>
                  {growth.reflection && <p style={reflectionStyles}>{growth.reflection}</p>}
                </div>
              ))}
            </div>
          </CardSection>
        </Card>
      )}

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
