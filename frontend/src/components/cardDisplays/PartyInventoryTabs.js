// PartyInventoryTabs.js - The "Your Party" section with a party/inventory toggle
// One view at a time: the active party's monster cards, or the paginated
// inventory (items + CoCaTok keepsakes). Used at home base; the dungeon
// panel carries its own copy of the toggle alongside run-specific tools.

import React, { useState } from 'react';
import PartyDisplay from './PartyDisplay.js';
import InventoryPanel from '../inventory/InventoryPanel.js';
import { Card, CardSection, Button } from '../../shared/ui/index.js';

function PartyInventoryTabs() {
  const [view, setView] = useState('party');

  return (
    <div>
      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginBottom: '12px' }}>
        <Button
          size="md"
          icon="🛡️"
          variant={view === 'party' ? 'primary' : 'secondary'}
          onClick={() => setView('party')}
        >
          Party
        </Button>
        <Button
          size="md"
          icon="🎒"
          variant={view === 'inventory' ? 'primary' : 'secondary'}
          onClick={() => setView('inventory')}
        >
          Inventory
        </Button>
      </div>

      {view === 'party' ? (
        <PartyDisplay />
      ) : (
        <Card>
          <CardSection title="🎒 Inventory" type="header" />
          <InventoryPanel />
        </Card>
      )}
    </div>
  );
}

export default PartyInventoryTabs;
