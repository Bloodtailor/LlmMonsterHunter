// DungeonEntryText.js - Minimal component for streaming dungeon entry text
// PERFORMANCE FOCUSED - Only subscribes to entryText, doesn't rerender on other events
// This is the healthy pattern: small, focused context consumers

import React, { useEffect } from 'react';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * DungeonEntryText component
 * Only handles streaming entry text display - minimal rerenders
 * Follows healthy pattern for context consumers
 */
function DungeonEntryText() {
  // Only consume what we need - just entryText
  const { entryText } = useDungeon();

  // Simple text display with basic styling
  const textStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    padding: '24px',
    minHeight: '200px',
    whiteSpace: 'pre-wrap', // Preserves line breaks and spaces
    fontFamily: 'var(--font-family-serif)', // More immersive for story text
  };

  const displayText = entryText || 'Preparing your dungeon entry...';

  return (
    <div style={textStyles}>
      {displayText}
    </div>
  );
}

export default DungeonEntryText;