// DungeonEntranceScreen.js - Pure layout component
// PERFORMANCE OPTIMIZED - NO context subscriptions, never rerenders on context changes  
// Completely layout-only, all context logic handled by child components

import React from 'react';
import { Card, CardSection } from '../../../shared/ui/index.js';

// Import focused components
import DungeonEntryText from '../components/DungeonEntryText.js';
import ContinueToDoorsButton from '../components/ContinueToDoorsButton.js';
import AutoEnterDungeonEffect from '../components/AutoEnterDungeonEffect.js';
import DungeonResetButton from '../components/DungeonResetButton.js';

/**
 * DungeonEntranceScreen component
 * Pure layout component with ZERO context subscriptions
 * Will never rerender due to dungeon context changes
 */
function DungeonEntranceScreen() {

  // Pure layout - never changes, never rerenders
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Side effect component - handles auto-enter logic */}
      <AutoEnterDungeonEffect />
      
      {/* Header */}
      <Card size="xl" background="light">
        <CardSection type="header" size="xl" title="🏰 Dungeon Entrance" alignment="center">
          <p>As you approach the ancient dungeon, mystical energies swirl around you...</p>
        </CardSection>
      </Card>

      {/* Entry Text - Focused component that handles streaming */}
      <Card size="xl" background="dark">
        <CardSection type="content" padding="none">
          <DungeonEntryText />
        </CardSection>
      </Card>

      {/* Continue Button - Focused component that handles state */}
      <Card size="xl" background="light">
        <CardSection type="content" alignment="center" padding="sm">
          <ContinueToDoorsButton />
          
          {/* Back button - Isolated component with context subscription */}
          <div style={{ marginTop: '16px' }}>
            <DungeonResetButton />
          </div>
        </CardSection>
      </Card>
    </div>
  );
}

export default DungeonEntranceScreen;
