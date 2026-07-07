// EncounterTextDisplay.js - Streaming vanity text for the encounter
// PERFORMANCE FOCUSED - Only subscribes to encounterText
// Same healthy pattern as DungeonEntryText: small, focused consumer

import React from 'react';
import { Card, CardSection } from '../../../shared/ui/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * EncounterTextDisplay component
 * Streams the arrival vanity text token by token - hidden until it starts
 */
function EncounterTextDisplay() {
  const { encounterText, exitText } = useDungeon();

  if (exitText || !encounterText) return null;

  const textStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    padding: '24px',
    whiteSpace: 'pre-wrap',
    fontFamily: 'var(--font-family-serif)',
  };

  return (
    <Card size="xl" background="dark">
      <CardSection type="content" padding="none">
        <div style={textStyles}>{encounterText}</div>
      </CardSection>
    </Card>
  );
}

export default EncounterTextDisplay;
