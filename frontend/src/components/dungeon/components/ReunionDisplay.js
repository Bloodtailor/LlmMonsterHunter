// ReunionDisplay.js - The party recognizes a monster they have met before
// PERFORMANCE FOCUSED - Only subscribes to reunionText/isReturningEncounter
// Streams the recognition scene with an unmistakable "it remembers you"
// banner above it - the payoff moment of the memory system

import React from 'react';
import { Card, CardSection, Badge } from '../../../shared/ui/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * ReunionDisplay component
 * Streams the moment of recognition when a remembered monster returns
 */
function ReunionDisplay() {
  const { reunionText, isReturningEncounter, exitText } = useDungeon();

  if (exitText || (!isReturningEncounter && !reunionText)) return null;

  const textStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    padding: '24px',
    whiteSpace: 'pre-wrap',
    fontFamily: 'var(--font-family-serif)',
    fontStyle: 'italic'
  };

  return (
    <Card size="xl" background="dark">
      <CardSection type="content" padding="none" alignment="center">
        <div style={{ paddingTop: '16px' }}>
          <Badge variant="warning" size="md" pill>
            🕯️ It remembers you
          </Badge>
        </div>
        {reunionText && (
          <div style={textStyles}>
            {reunionText}
          </div>
        )}
      </CardSection>
    </Card>
  );
}

export default ReunionDisplay;
