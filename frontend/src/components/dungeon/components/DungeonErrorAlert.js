// DungeonErrorAlert.js - Shows dungeon errors instead of hanging silently
// PERFORMANCE FOCUSED - Only consumes isError/error
// Renders nothing when everything is fine

import React from 'react';
import { Alert } from '../../../shared/ui/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * DungeonErrorAlert component
 * Surfaces workflow/API errors on the dungeon screens
 */
function DungeonErrorAlert() {
  const { isError, error } = useDungeon();

  if (!isError) return null;

  return (
    <Alert type="error" title="Something went wrong in the dungeon">
      {String(error || 'Unknown error')}
    </Alert>
  );
}

export default DungeonErrorAlert;
