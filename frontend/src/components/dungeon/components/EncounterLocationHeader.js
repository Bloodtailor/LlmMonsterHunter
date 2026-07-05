// EncounterLocationHeader.js - Shows where the party has arrived
// PERFORMANCE FOCUSED - Only consumes currentLocation
// Shows a traveling state until the arrival location is generated

import React from 'react';
import { Card, CardSection, LoadingSpinner } from '../../../shared/ui/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * EncounterLocationHeader component
 * Traveling indicator until location_generated arrives, then the location
 */
function EncounterLocationHeader() {
  const { currentLocation, exitText } = useDungeon();

  // The exit view owns the screen when the party is leaving
  if (exitText) return null;

  if (!currentLocation) {
    return (
      <Card size="xl" background="light">
        <CardSection type="content" alignment="center">
          <LoadingSpinner size="section" type="spin" />
          <p style={{ marginTop: '16px', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
            You venture down the path...
          </p>
        </CardSection>
      </Card>
    );
  }

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="xl" title={`📍 ${currentLocation.name}`} alignment="center">
        <p>{currentLocation.description}</p>
      </CardSection>
    </Card>
  );
}

export default EncounterLocationHeader;
