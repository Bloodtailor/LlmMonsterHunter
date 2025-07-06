// Dungeon Screen - Complete Adventure Experience
// Handles dungeon entry, door choices, event text, and navigation
// Shows persistent party display and manages dungeon state

import React, { useState, useEffect } from 'react';
import MonsterCard from '../game/MonsterCard';
import { enterDungeon, chooseDoor, getDungeonState, isInDungeon } from '../../services/dungeonApi';

function DungeonScreen({ onReturnToHomeBase }) {
  // Dungeon state
  const [dungeonState, setDungeonState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [processingChoice, setProcessingChoice] = useState(false);
  
  // UI state
  const [showEventText, setShowEventText] = useState(false);
  const [eventText, setEventText] = useState('');
  const [showExitText, setShowExitText] = useState(false);
  const [exitText, setExitText] = useState('');

  // Load dungeon state on component mount
  useEffect(() => {
    initializeDungeon();
  }, []);

  /**
   * Initialize dungeon - either enter new dungeon or load existing state
   */
  const initializeDungeon = async () => {
    setLoading(true);
    setError(null);

    try {
      // First check if already in dungeon
      const stateResponse = await getDungeonState();
      
      if (stateResponse.success && stateResponse.in_dungeon) {
        // Already in dungeon, load existing state
        console.log('📍 Loading existing dungeon state');
        setDungeonState(stateResponse.state);
      } else {
        // Enter new dungeon
        console.log('🏰 Entering new dungeon');
        const enterResponse = await enterDungeon();
        
        if (enterResponse.success) {
          setDungeonState({
            entry_text: enterResponse.entry_text,
            current_location: enterResponse.location,
            available_doors: enterResponse.doors,
            party_summary: enterResponse.party_summary,
            last_event_text: null
          });
          console.log('✅ Successfully entered dungeon');
        } else {
          throw new Error(enterResponse.error || 'Failed to enter dungeon');
        }
      }
    } catch (err) {
      console.error('❌ Failed to initialize dungeon:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle door choice selection
   */
  const handleDoorChoice = async (doorChoice) => {
    if (processingChoice) return;

    setProcessingChoice(true);
    setShowEventText(false);
    setShowExitText(false);

    try {
      console.log(`🚪 Choosing door: ${doorChoice}`);
      const response = await chooseDoor(doorChoice);

      if (response.success) {
        if (response.dungeon_completed || response.in_dungeon === false) {
          // Exit door chosen - show exit text
          setExitText(response.exit_text || 'You have successfully left the dungeon!');
          setShowExitText(true);
          console.log('🏠 Exited dungeon successfully');
        } else {
          // Location door chosen - show event text and update state
          setEventText(response.event_text || 'You explore the new location...');
          setShowEventText(true);
          
          // Update dungeon state with new location and doors
          setDungeonState(prev => ({
            ...prev,
            current_location: response.new_location || prev.current_location,
            available_doors: response.new_doors || [],
            last_event_text: response.event_text
          }));
          
          console.log('📍 Moved to new location:', response.new_location?.name);
        }
      } else {
        throw new Error(response.error || 'Failed to choose door');
      }
    } catch (err) {
      console.error('❌ Error choosing door:', err);
      setError(`Failed to choose door: ${err.message}`);
    } finally {
      setProcessingChoice(false);
    }
  };

  /**
   * Handle continuing after event text
   */
  const handleContinue = () => {
    setShowEventText(false);
    setEventText('');
  };

  /**
   * Handle returning to home base after exiting dungeon
   */
  const handleReturnHome = () => {
    if (onReturnToHomeBase) {
      onReturnToHomeBase();
    }
  };

  /**
   * Get door button styling based on door type
   */
  const getDoorButtonClass = (door) => {
    if (door.type === 'exit') {
      return 'door-button door-exit';
    }
    return 'door-button door-location';
  };

  // Loading state
  if (loading) {
    return (
      <div className="dungeon-screen">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="loading-text">Entering the dungeon...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="dungeon-screen">
        <div className="error-container">
          <h2>❌ Dungeon Error</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={initializeDungeon} className="btn btn-primary">
              🔄 Try Again
            </button>
            <button onClick={handleReturnHome} className="btn btn-secondary">
              🏠 Return Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Exit text state
  if (showExitText) {
    return (
      <div className="dungeon-screen">
        <div className="dungeon-content">
          <div className="dungeon-header">
            <h1>🏰 Dungeon Adventure</h1>
            <div className="party-display">
              <span className="party-label">Party: {dungeonState?.party_summary || 'Unknown'}</span>
            </div>
          </div>

          <div className="exit-text-container">
            <div className="exit-text-content">
              <h2>🌅 Dungeon Exit</h2>
              <div className="exit-text">
                {exitText}
              </div>
              <div className="exit-actions">
                <button 
                  onClick={handleReturnHome}
                  className="btn btn-primary btn-lg"
                >
                  🏠 Return to Home Base
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Event text state
  if (showEventText) {
    return (
      <div className="dungeon-screen">
        <div className="dungeon-content">
          <div className="dungeon-header">
            <h1>🏰 Dungeon Adventure</h1>
            <div className="party-display">
              <span className="party-label">Party: {dungeonState?.party_summary || 'Unknown'}</span>
            </div>
          </div>

          <div className="event-text-container">
            <div className="event-text-content">
              <h2>⚡ Adventure Event</h2>
              <div className="event-text">
                {eventText}
              </div>
              <div className="event-actions">
                <button 
                  onClick={handleContinue}
                  className="btn btn-primary btn-lg"
                >
                  ➡️ Continue
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main dungeon exploration state
  return (
    <div className="dungeon-screen">
      <div className="dungeon-content">
        {/* Dungeon Header with Party */}
        <div className="dungeon-header">
          <h1>🏰 Dungeon Adventure</h1>
          <div className="party-display">
            <span className="party-label">Party: {dungeonState?.party_summary || 'Unknown'}</span>
          </div>
        </div>

        {/* Entry Text (first time entering) */}
        {dungeonState?.entry_text && !dungeonState?.last_event_text && (
          <div className="entry-text-section">
            <h2>🌟 Dungeon Entry</h2>
            <div className="entry-text">
              {dungeonState.entry_text}
            </div>
          </div>
        )}

        {/* Current Location */}
        <div className="location-section">
          <h2>📍 {dungeonState?.current_location?.name || 'Unknown Location'}</h2>
          <div className="location-description">
            {dungeonState?.current_location?.description || 'You find yourself in a mysterious place...'}
          </div>
        </div>

        {/* Door Choices */}
        <div className="doors-section">
          <h3>🚪 Choose Your Path</h3>
          <div className="doors-grid">
            {dungeonState?.available_doors?.map((door, index) => (
              <button
                key={door.id || index}
                className={getDoorButtonClass(door)}
                onClick={() => handleDoorChoice(door.id)}
                disabled={processingChoice}
              >
                <div className="door-name">{door.name}</div>
                <div className="door-description">{door.description}</div>
              </button>
            )) || (
              <div className="no-doors">
                <p>No doors available. Something went wrong...</p>
                <button onClick={initializeDungeon} className="btn btn-secondary">
                  🔄 Reload Dungeon
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Processing state */}
        {processingChoice && (
          <div className="processing-overlay">
            <div className="processing-content">
              <div className="loading-spinner"></div>
              <p>Processing your choice...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DungeonScreen;