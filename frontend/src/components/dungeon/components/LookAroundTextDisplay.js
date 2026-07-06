// LookAroundTextDisplay.js - Streaming look-around text for explore arrivals
// PERFORMANCE FOCUSED - Only subscribes to lookText
// Same healthy pattern as EncounterTextDisplay: small, focused consumer

import React from 'react';
import { Card, CardSection } from '../../../shared/ui/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * LookAroundTextDisplay component
 * Streams the party taking in a new location token by token
 */
function LookAroundTextDisplay() {
  const { lookText, exitText } = useDungeon();

  if (exitText || !lookText) return null;

  const textStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    padding: '24px',
    whiteSpace: 'pre-wrap',
    fontFamily: 'var(--font-family-serif)'
  };

  return (
    <Card size="xl" background="dark">
      <CardSection type="content" padding="none">
        <div style={textStyles}>
          {lookText}
        </div>
      </CardSection>
    </Card>
  );
}

export default LookAroundTextDisplay;
