// DungeonDoorsScreen.js - Path selection screen with clickable path cards
// Shows the paths onward from the current location. Each path hides a
// pre-assigned event the player cannot see - choose wisely.

import React from 'react';
import { Card, CardSection, Button, Badge, LoadingSpinner } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

/**
 * DungeonDoorsScreen component
 * Displays clickable path cards for dungeon navigation
 * Exit paths are visibly marked; everything else is a mystery
 */
function DungeonDoorsScreen() {
  const { navigateToGameScreen } = useNavigation();
  const { currentLocation, paths, arePathsReady, choosePath, resetDungeon } = useDungeon();

  // Take a path: queue the workflow and move to the location screen
  const handlePathClick = (path) => {
    choosePath(path.id);
    navigateToGameScreen('dungeon-location');
  };

  // Process paths object into array
  const processPaths = (pathsObject) => {
    if (!pathsObject) return [];

    const pathEntries = [];
    Object.entries(pathsObject).forEach(([key, value]) => {
      if (typeof value === 'object' && value.type) {
        pathEntries.push({
          id: key,
          ...value
        });
      }
    });

    return pathEntries;
  };

  const pathArray = processPaths(paths);

  // Get icon and badge variant for path type
  const getPathTypeInfo = (type) => {
    switch (type) {
      case 'path':
        return { icon: '🧭', variant: 'primary', label: 'Path' };
      case 'exit':
        return { icon: '🚪', variant: 'secondary', label: 'Way Out' };
      default:
        return { icon: '❓', variant: 'tertiary', label: 'Unknown' };
    }
  };

  // Card click styles
  const pathCardStyles = {
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    border: '2px solid transparent'
  };

  const pathCardHoverStyles = {
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
    borderColor: 'var(--color-primary)'
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header - where the party currently stands */}
      <Card size="xl" background="light">
        <CardSection
          type="header"
          size="xl"
          title={`📍 ${currentLocation?.name || 'Somewhere in the Dungeon'}`}
          alignment="center"
        >
          <p>{currentLocation?.description || ''}</p>
          <p style={{ marginTop: '8px', fontStyle: 'italic', color: 'var(--color-text-muted)' }}>
            The paths ahead reveal nothing of what waits beyond them.
          </p>
        </CardSection>
      </Card>

      {/* Path Cards */}
      {!arePathsReady ? (
        <Card size="xl" background="light">
          <CardSection type="content" alignment="center">
            <LoadingSpinner size="section" type="spin" />
            <p style={{ marginTop: '16px', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
              Scouting the paths ahead...
            </p>
          </CardSection>
        </Card>
      ) : pathArray.length > 0 ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '24px'
        }}>
          {pathArray.map((path) => {
            const typeInfo = getPathTypeInfo(path.type);

            return (
              <Card
                key={path.id}
                size="lg"
                background="dark"
                style={pathCardStyles}
                onClick={() => handlePathClick(path)}
                onMouseEnter={(e) => {
                  Object.assign(e.currentTarget.style, pathCardHoverStyles);
                }}
                onMouseLeave={(e) => {
                  Object.assign(e.currentTarget.style, pathCardStyles);
                }}
              >
                <CardSection type="header" size="lg" alignment="center">
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    justifyContent: 'center',
                    flexWrap: 'wrap'
                  }}>
                    <span style={{ fontSize: '2rem' }}>{typeInfo.icon}</span>
                    <Badge variant={typeInfo.variant} size="md">
                      {typeInfo.label}
                    </Badge>
                  </div>
                  <h3 style={{
                    margin: '8px 0 0 0',
                    fontSize: 'var(--font-size-lg)',
                    color: 'var(--color-text-primary)'
                  }}>
                    {path.name}
                  </h3>
                </CardSection>

                <CardSection type="content" alignment="center">
                  <p style={{
                    color: 'var(--color-text-secondary)',
                    lineHeight: 'var(--line-height-relaxed)',
                    fontSize: 'var(--font-size-md)',
                    textAlign: 'center'
                  }}>
                    {path.description}
                  </p>
                </CardSection>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card size="xl" background="light">
          <CardSection type="content" alignment="center">
            <p style={{ color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
              No paths available. Something may have gone wrong with the dungeon generation.
            </p>
          </CardSection>
        </Card>
      )}

      {/* Navigation */}
      <Card size="xl" background="light">
        <CardSection type="content" alignment="center">
          <Button
            size="lg"
            variant="secondary"
            onClick={() => {
              resetDungeon();
              navigateToGameScreen('homebase');
            }}
          >
            🏠 Abandon Quest
          </Button>
        </CardSection>
      </Card>
    </div>
  );
}

export default DungeonDoorsScreen;
