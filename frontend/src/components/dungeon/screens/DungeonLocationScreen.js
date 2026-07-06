// DungeonLocationScreen.js - Pure layout component for arriving at a location
// PERFORMANCE OPTIMIZED - NO context subscriptions, never rerenders on context changes
// The encounter unfolds top to bottom as each child's data arrives:
// traveling -> location -> vanity/look text streams -> monster reveals ->
// dialogue / explore choices / battle intro. The party rides along at the
// bottom, always visible, abilities ready.

import React from 'react';

// Import focused components - each decides its own visibility from context
import EncounterLocationHeader from '../components/EncounterLocationHeader.js';
import EncounterTextDisplay from '../components/EncounterTextDisplay.js';
import LookAroundTextDisplay from '../components/LookAroundTextDisplay.js';
import EncounterMonsterDisplay from '../components/EncounterMonsterDisplay.js';
import ExplorePanel from '../components/ExplorePanel.js';
import MonsterDialogueBox from '../components/MonsterDialogueBox.js';
import BattleIntroBox from '../components/BattleIntroBox.js';
import DungeonPartyPanel from '../components/DungeonPartyPanel.js';
import DungeonExitView from '../components/DungeonExitView.js';
import DungeonErrorAlert from '../components/DungeonErrorAlert.js';

/**
 * DungeonLocationScreen component
 * Pure layout with ZERO context subscriptions
 * Children appear as their pieces of the encounter finish generating
 */
function DungeonLocationScreen() {

  // Pure layout - never changes, never rerenders
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Errors surface here instead of hanging the screen */}
      <DungeonErrorAlert />

      {/* Exit branch - owns the screen when the party takes an exit path */}
      <DungeonExitView />

      {/* Where the party arrived (traveling indicator until generated) */}
      <EncounterLocationHeader />

      {/* Streaming vanity text - the presence in the shadows (encounters) */}
      <EncounterTextDisplay />

      {/* Streaming look-around text (explore arrivals) */}
      <LookAroundTextDisplay />

      {/* The monsters' cards - appear on creation, art pops in live */}
      <EncounterMonsterDisplay />

      {/* Explore choices - talk / surprise attack / sneak, or camp / continue */}
      <ExplorePanel />

      {/* The conversation - the monster asks, the party answers, the LLM decides */}
      <MonsterDialogueBox />

      {/* The battle challenge - the enemies confront you, then to battle */}
      <BattleIntroBox />

      {/* The party - always visible, any ability on anything */}
      <DungeonPartyPanel />
    </div>
  );
}

export default DungeonLocationScreen;
