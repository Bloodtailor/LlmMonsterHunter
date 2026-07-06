// BattleSideDisplay.js - One side of the battlefield
// Enemies come from the dungeon encounter reveal; allies from the party

import React from 'react';
import { Card, CardSection } from '../../../shared/ui/index.js';
import BattleMonsterTile from './BattleMonsterTile.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';
import { useParty } from '../../../app/contexts/PartyContext/index.js';

/**
 * BattleSideDisplay component
 * @param {string} side - 'enemies' | 'allies'
 */
function BattleSideDisplay({ side }) {
  const { displayedBattle } = useBattleContext();
  const { encounterMonsters } = useDungeon();
  const { partyMonsters } = useParty();

  const entries = displayedBattle?.[side] || {};
  if (Object.keys(entries).length === 0) return null;

  // Full monster objects for the cards
  const pool = side === 'enemies' ? (encounterMonsters || []) : (partyMonsters || []);
  const findMonster = (monsterId) => pool.find(m => String(m.id) === String(monsterId)) || null;

  return (
    <Card size="xl" background={side === 'enemies' ? 'dark' : 'light'}>
      <CardSection
        type="header"
        size="md"
        title={side === 'enemies' ? '👹 Hostile Monsters' : '🛡️ Your Party'}
        alignment="center"
      />
      <CardSection type="content" alignment="center">
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          {Object.entries(entries).map(([monsterId, entry]) => (
            <BattleMonsterTile
              key={monsterId}
              monster={findMonster(monsterId)}
              entry={entry}
            />
          ))}
        </div>
      </CardSection>
    </Card>
  );
}

export default BattleSideDisplay;
