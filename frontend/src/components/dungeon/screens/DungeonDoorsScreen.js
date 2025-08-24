// DungeonDoorsScreen.js - Door selection screen with clickable door cards
// Shows doors from workflow completion and handles door selection
// Location doors and exit doors for now both return to home base

import React from 'react';
import { Card, CardSection, Button, Badge } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

/**
 * DungeonDoorsScreen component
 * Displays clickable door cards for dungeon navigation
 * Handles location doors and exit doors
 */
function DungeonDoorsScreen() {
  const { navigateToGameScreen } = useNavigation();
  const { doors, resetDungeon } = useDungeon();

  // Handle location door selection
  const handleLocationDoor = (doorData) => {
    console.log('Selected location door:', doorData.name);
    // TODO: Navigate to location-specific screen
    // For now, return to home base
    resetDungeon();
    navigateToGameScreen('homebase');
  };

  // Handle exit door selection  
  const handleExitDoor = (doorData) => {
    console.log('Selected exit door:', doorData.name);
    // TODO: Handle dungeon exit logic
    // For now, return to home base
    resetDungeon();
    navigateToGameScreen('homebase');
  };

  // Process doors object into array
  const processDoors = (doorsObject) => {
    if (!doorsObject) return [];
    
    const doorEntries = [];
    Object.entries(doorsObject).forEach(([key, value]) => {
      // Skip the success property
      if (key !== 'success' && typeof value === 'object' && value.type) {
        doorEntries.push({
          id: key,
          ...value
        });
      }
    });
    
    return doorEntries;
  };

  const doorArray = processDoors(doors);

  // Handle door click based on type
  const handleDoorClick = (door) => {
    if (door.type === 'location') {
      handleLocationDoor(door);
    } else if (door.type === 'exit') {
      handleExitDoor(door);
    }
  };

  // Get icon and badge variant for door type
  const getDoorTypeInfo = (type) => {
    switch (type) {
      case 'location':
        return { icon: '🗺️', variant: 'primary', label: 'Location' };
      case 'exit':
        return { icon: '🚪', variant: 'secondary', label: 'Exit' };
      default:
        return { icon: '❓', variant: 'tertiary', label: 'Unknown' };
    }
  };

  // Card click styles
  const doorCardStyles = {
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    border: '2px solid transparent'
  };

  const doorCardHoverStyles = {
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
    borderColor: 'var(--color-primary)'
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <Card size="xl" background="light">
        <CardSection type="header" size="xl" title="🚪 Choose Your Path" alignment="center">
          <p>Three paths lie before you. Choose wisely, adventurer.</p>
        </CardSection>
      </Card>

      {/* Door Cards */}
      {doorArray.length > 0 ? (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '24px' 
        }}>
          {doorArray.map((door) => {
            const typeInfo = getDoorTypeInfo(door.type);
            
            return (
              <Card 
                key={door.id}
                size="lg" 
                background="dark"
                style={doorCardStyles}
                onClick={() => handleDoorClick(door)}
                onMouseEnter={(e) => {
                  Object.assign(e.currentTarget.style, doorCardHoverStyles);
                }}
                onMouseLeave={(e) => {
                  Object.assign(e.currentTarget.style, doorCardStyles);
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
                    {door.name}
                  </h3>
                </CardSection>
                
                <CardSection type="content" alignment="center">
                  <p style={{
                    color: 'var(--color-text-secondary)',
                    lineHeight: 'var(--line-height-relaxed)',
                    fontSize: 'var(--font-size-md)',
                    textAlign: 'center'
                  }}>
                    {door.description}
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
              No doors available. Something may have gone wrong with the dungeon generation.
            </p>
          </CardSection>
        </Card>
      )}

      {/* Navigation */}
      <Card size="xl" background="light">
        <CardSection type="content" alignment="center">
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Button 
              size="lg" 
              variant="tertiary"
              onClick={() => navigateToGameScreen('dungeon-entrance')}
            >
              ← Back to Entrance
            </Button>
            
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
          </div>
        </CardSection>
      </Card>
    </div>
  );
}

export default DungeonDoorsScreen;