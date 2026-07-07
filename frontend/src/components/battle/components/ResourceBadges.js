// ResourceBadges.js - Stamina/mana reserve badges (word ladders, no numbers)
// Shared by battle tiles and the dungeon party panel. Levels come from the
// backend's RESOURCE_LADDER: brimming > steady > strained > drained > spent.
// Reserves refill only when the party enters the dungeon (and at camp).

import React from 'react';
import { Badge } from '../../../shared/ui/index.js';

// Reserve level -> badge look (mirrors the condition badge treatment)
const RESOURCE_VARIANTS = {
  brimming: 'success',
  steady: 'info',
  strained: 'warning',
  drained: 'warning',
  spent: 'error'
};

/**
 * ResourceBadges component - two small badges: 💪 stamina and ✨ mana
 * Renders nothing when no levels are known (e.g. outside a run).
 * @param {string} stamina - Reserve word for the stamina pool
 * @param {string} mana - Reserve word for the mana pool
 */
function ResourceBadges({ stamina, mana }) {
  if (!stamina && !mana) return null;

  return (
    <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
      {stamina && (
        <Badge variant={RESOURCE_VARIANTS[stamina] || 'info'} size="sm">
          💪 {stamina}
        </Badge>
      )}
      {mana && (
        <Badge variant={RESOURCE_VARIANTS[mana] || 'info'} size="sm">
          ✨ {mana}
        </Badge>
      )}
    </div>
  );
}

export default ResourceBadges;
