// TreasureDisplay.js - A treasure path paid out: streamed discovery
// narration plus the item now sitting in the party's inventory

import React from 'react';
import { Card, CardSection, Badge } from '../../../shared/ui/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

function TreasureDisplay() {
  const { treasureText, treasureItem, exitText } = useDungeon();

  if (exitText || (!treasureText && !treasureItem)) return null;

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="md" title="💰 Treasure!" alignment="center" />

      {treasureText && (
        <CardSection type="content" alignment="center">
          <p style={{
            fontSize: 'var(--font-size-md)',
            lineHeight: 'var(--line-height-relaxed)',
            color: 'var(--color-text-primary)',
            fontFamily: 'var(--font-family-serif)',
            fontStyle: 'italic',
            whiteSpace: 'pre-wrap',
            maxWidth: '640px',
            margin: '0 auto'
          }}>
            {treasureText}
          </p>
        </CardSection>
      )}

      {treasureItem && (
        <CardSection type="content" alignment="center">
          <div style={{
            display: 'inline-flex',
            gap: '12px',
            alignItems: 'center',
            padding: '12px 20px',
            borderRadius: 'var(--radius-sm, 8px)',
            background: 'var(--color-surface-secondary, rgba(0,0,0,0.15))'
          }}>
            <span style={{ fontSize: '2rem', lineHeight: 1 }}>{treasureItem.emoji || '🎁'}</span>
            <div style={{ textAlign: 'left' }}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                  {treasureItem.name}
                </span>
                <Badge variant="info" size="sm" pill>
                  {treasureItem.uses_remaining ?? treasureItem.usesRemaining ?? 1} use(s)
                </Badge>
              </div>
              <p style={{
                margin: '4px 0 0',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-secondary)',
                maxWidth: '480px'
              }}>
                {treasureItem.description}
              </p>
            </div>
          </div>
          <p style={{
            margin: '10px 0 0',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-muted)'
          }}>
            Added to your inventory.
          </p>
        </CardSection>
      )}
    </Card>
  );
}

export default TreasureDisplay;
