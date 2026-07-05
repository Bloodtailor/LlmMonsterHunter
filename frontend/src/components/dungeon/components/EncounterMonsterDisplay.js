// EncounterMonsterDisplay.js - The monster's dramatic reveal
// PERFORMANCE FOCUSED - Only consumes encounterMonster
// Reuses MonsterCard: the card appears when the monster is created,
// then abilities and art pop in live via the monster domain events

import React from 'react';
import MonsterCard from '../../cards/MonsterCard.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * EncounterMonsterDisplay component
 * Shows the encounter monster's card as it comes into existence
 */
function EncounterMonsterDisplay() {
  const { encounterMonster, exitText } = useDungeon();

  if (exitText || !encounterMonster) return null;

  return (
    <div style={{ display: 'flex', justifyContent: 'center' }}>
      <MonsterCard
        monster={encounterMonster}
        size="lg"
      />
    </div>
  );
}

export default EncounterMonsterDisplay;
