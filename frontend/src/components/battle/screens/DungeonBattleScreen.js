// DungeonBattleScreen.js - Pure layout component for battles
// PERFORMANCE OPTIMIZED - NO context subscriptions, never rerenders on context changes
// Children decide their own visibility: selection panel during 'selecting',
// battle log during processing, outcome view once it's all been read

import React from 'react';

import BattleOutcomeView from '../components/BattleOutcomeView.js';
import BattleSideDisplay from '../components/BattleSideDisplay.js';
import BattleLogBox from '../components/BattleLogBox.js';
import ActionSelectionPanel from '../components/ActionSelectionPanel.js';

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

      {/* Action selection - visible only while the round awaits orders */}
      <ActionSelectionPanel />
    </div>
  );
}

export default DungeonBattleScreen;
