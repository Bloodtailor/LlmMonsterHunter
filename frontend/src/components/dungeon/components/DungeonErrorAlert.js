// DungeonErrorAlert.js - Shows dungeon errors instead of hanging silently
// PERFORMANCE FOCUSED - Only consumes isError/error
// Renders nothing when everything is fine
//
// It also carries the run's ESCAPE HATCH. A failed workflow leaves the
// screen with no result to render: no encounter panel, no dialogue box,
// and a "Continue to the Paths" button still disabled because the paths
// never arrived. That is how a real expedition became unplayable after a
// single generation returned prose instead of JSON. The backend now
// degrades instead of raising, but any future failure - a dropped
// connection, a timeout - would strand the player the same way, so the
// error itself now offers the way onward.

import React from 'react';
import { Alert, Button } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * DungeonErrorAlert component
 * Surfaces workflow/API errors on the dungeon screens, with a way out
 */
function DungeonErrorAlert() {
  const { isError, error, continueExploring } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  if (!isError) return null;

  // Look around from where the party stands - the one action that always
  // regenerates paths, whatever went wrong before it
  const handleLookAround = () => {
    continueExploring();
    navigateToGameScreen('dungeon-doors');
  };

  return (
    <Alert type="error" title="Something went wrong in the dungeon">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <span>{String(error || 'Unknown error')}</span>
        <span style={{ color: 'var(--color-text-secondary)' }}>
          The expedition can go on - look around from here for fresh paths.
        </span>
        <div>
          <Button size="md" icon="🧭" variant="primary" onClick={handleLookAround}>
            Look Around
          </Button>
        </div>
      </div>
    </Alert>
  );
}

export default DungeonErrorAlert;
