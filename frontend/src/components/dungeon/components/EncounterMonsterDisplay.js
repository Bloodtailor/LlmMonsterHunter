// EncounterMonsterDisplay.js - The monsters' dramatic reveal
// PERFORMANCE FOCUSED - Only consumes encounterMonsters
// Reuses MonsterCard: cards appear as monsters are created,
// then abilities and art pop in live via the monster domain events

import React from 'react';
import MonsterCard from '../../cards/MonsterCard.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * EncounterMonsterDisplay component
 * Shows each encounter monster's card as it comes into existence
 * (riddles reveal one; battles reveal the whole hostile group)
 */
function EncounterMonsterDisplay() {
  const { encounterMonsters, exitText } = useDungeon();

  if (exitText || !encounterMonsters || encounterMonsters.length === 0) return null;

  return (
    <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', flexWrap: 'wrap' }}>
      {encounterMonsters.map(monster => (
        <MonsterCard
          key={monster.id}
          monster={monster}
          size="lg"
        />
      ))}
    </div>
  );
}

export default EncounterMonsterDisplay;
