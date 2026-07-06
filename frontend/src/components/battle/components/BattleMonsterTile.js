// BattleMonsterTile.js - One combatant: compact card + condition badge
// Condition comes from the DISPLAYED battle (which lags the backend so
// the badges change in step with the revealed story)

import React from 'react';
import MonsterCard from '../../cards/MonsterCard.js';
import { Badge, Card, CardSection } from '../../../shared/ui/index.js';

// Condition ladder -> badge look
const CONDITION_VARIANTS = {
  fresh: 'success',
  scuffed: 'info',
  wounded: 'warning',
  battered: 'warning',
  critical: 'error',
  incapacitated: 'error'
};

/**
 * BattleMonsterTile component
 * @param {object} monster - Full transformed monster object (may be null)
 * @param {object} entry - Battle entry {name, condition, defending}
 */
function BattleMonsterTile({ monster, entry }) {
  const condition = entry?.condition || 'fresh';
  const isDown = condition === 'incapacitated';

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '8px',
      opacity: isDown ? 0.4 : 1,
      transition: 'opacity 0.4s ease'
    }}>
      {monster ? (
        <MonsterCard monster={monster} size="sm" hideFlipHint={true} />
      ) : (
        <Card size="sm">
          <CardSection type="content" alignment="center">
            {entry?.name || 'Unknown'}
          </CardSection>
        </Card>
      )}

      <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
        <Badge variant={CONDITION_VARIANTS[condition] || 'info'} size="sm">
          {condition}
        </Badge>
        {entry?.defending && !isDown && (
          <Badge variant="secondary" size="sm">🛡️ defending</Badge>
        )}
      </div>
    </div>
  );
}

export default BattleMonsterTile;
