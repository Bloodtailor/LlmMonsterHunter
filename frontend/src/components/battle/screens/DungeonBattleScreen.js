// DungeonBattleScreen.js - Pure layout component for battles
// PERFORMANCE OPTIMIZED - NO context subscriptions, never rerenders on context changes
// Children decide their own visibility: selection panel during 'selecting',
// battle log during processing, outcome view once it's all been read

import React from 'react';

import BattleOutcomeView from '../components/BattleOutcomeView.js';
import BattleSideDisplay from '../components/BattleSideDisplay.js';
import BattleLogBox from '../components/BattleLogBox.js';
import TurnPanel from '../components/TurnPanel.js';
import TalkResponsePanel from '../components/TalkResponsePanel.js';

/**
 * DungeonBattleScreen component
 * Pure layout with ZERO context subscriptions
 */
function DungeonBattleScreen() {
  // Pure layout - never changes, never rerenders
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Victory/defeat - takes over after the story is read */}
      <BattleOutcomeView />

      {/* The hostile side */}
      <BattleSideDisplay side="enemies" />

      {/* The referee's click-through narration */}
      <BattleLogBox />

      {/* Your side */}
      <BattleSideDisplay side="allies" />

      {/* One monster's turn - visible when an ally awaits orders */}
      <TurnPanel />

      {/* An enemy is talking - the player must respond */}
      <TalkResponsePanel />
    </div>
  );
}

export default DungeonBattleScreen;
