// DungeonLocationScreen.js - Pure layout component for arriving at a location
// PERFORMANCE OPTIMIZED - NO context subscriptions, never rerenders on context changes
// The encounter unfolds top to bottom as each child's data arrives:
// traveling -> location -> vanity text streams -> monster reveals -> riddle

import React from 'react';

// Import focused components - each decides its own visibility from context
import EncounterLocationHeader from '../components/EncounterLocationHeader.js';
import EncounterTextDisplay from '../components/EncounterTextDisplay.js';
import EncounterMonsterDisplay from '../components/EncounterMonsterDisplay.js';
import RiddleBox from '../components/RiddleBox.js';
import DungeonExitView from '../components/DungeonExitView.js';

/**
 * DungeonLocationScreen component
 * Pure layout with ZERO context subscriptions
 * Children appear as their pieces of the encounter finish generating
 */
function DungeonLocationScreen() {

  // Pure layout - never changes, never rerenders
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Exit branch - owns the screen when the party takes an exit path */}
      <DungeonExitView />

      {/* Where the party arrived (traveling indicator until generated) */}
      <EncounterLocationHeader />

      {/* Streaming vanity text - the presence in the shadows */}
      <EncounterTextDisplay />

      {/* The monster's card - appears on creation, art pops in live */}
      <EncounterMonsterDisplay />

      {/* The riddle challenge - question, answer, verdict, continue */}
      <RiddleBox />
    </div>
  );
}

export default DungeonLocationScreen;
