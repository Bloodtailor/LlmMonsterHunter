// GrowthDisplay.js - Growth reflections from camp spotlights
// PERFORMANCE FOCUSED - Only subscribes to growthResults
// After the camp scene, the spotlit monsters' reflections appear here:
// what they lived, what grew, any new or reworded abilities
// (exit-ceremony growth renders inside DungeonExitView instead)

import React from 'react';
import { Card, CardSection, Badge } from '../../../shared/ui/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

// Small badges for what a reflection actually changed
function growthBadges(growth) {
  const badges = [];
  if (growth.stat) {
    badges.push({ icon: '📈', text: `${growth.stat} +${growth.tier}` });
  }
  if (growth.new_ability) {
    badges.push({ icon: '⚡', text: `learned ${growth.new_ability}` });
  }
  if (growth.reworded_ability) {
    badges.push({ icon: '✍️', text: `${growth.reworded_ability} reworded` });
  }
  return badges;
}

/**
 * GrowthDisplay component
 * The campfire's quiet moments of growth, one block per spotlit monster
 */
function GrowthDisplay() {
  const { growthResults, exitText, hasCamped } = useDungeon();

  // Camp growth only - the exit view owns its own ceremony display
  if (exitText || !hasCamped || !growthResults || growthResults.length === 0) return null;

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
    <Card size="xl" background="dark">
      <CardSection type="header" size="md" title="🌱 By the fire, something settles" alignment="center" />
      <CardSection type="content">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '720px', margin: '0 auto' }}>
          {growthResults.map((growth) => (
            <div key={growth.monster_id} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap' }}>
                <strong>{growth.monster_name}</strong>
                {growthBadges(growth).map((badge, index) => (
                  <Badge key={index} variant="success" size="sm" pill>
                    {badge.icon} {badge.text}
                  </Badge>
                ))}
              </div>
              {growth.reflection && <p style={reflectionStyles}>{growth.reflection}</p>}
            </div>
          ))}
        </div>
      </CardSection>
    </Card>
  );
}

export default GrowthDisplay;
