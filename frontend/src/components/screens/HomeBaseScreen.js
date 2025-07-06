// Home Base Screen - WITH PARTY MANAGEMENT
// Displays following monsters and active party with click-to-toggle functionality
// Handles party management without interfering with card flip functionality

import React, { useState, useEffect } from 'react';
import MonsterCard from '../game/MonsterCard';
import { PartyToggleButton, usePartyManager } from '../game/PartyManager';
import { getGameState, getFollowingMonsters, getActiveParty, isPartyReady } from '../../services/gameStateApi';

function HomeBaseScreen({ onEnterDungeon }) {
  // State management
  const [gameState, setGameState] = useState(null);
  const [followingMonsters, setFollowingMonsters] = useState([]);
  const [activeParty, setActiveParty] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [partyReady, setPartyReady] = useState(false);

  // Pagination state for following monsters
  const [currentPage, setCurrentPage] = useState(1);
  const monstersPerPage = 12;

  // Party management hook
  const { addToParty, removeFromParty, updating } = usePartyManager(({ party, ready }) => {
    setActiveParty(party);
    setPartyReady(ready);
  });

  // Load data on component mount
  useEffect(() => {
    loadHomeBaseData();
  }, []);

  /**
   * Load all home base data from APIs
   */
  const loadHomeBaseData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load game state and following monsters
      const [gameStateResponse, followingResponse, partyResponse, readyResponse] = await Promise.all([
        getGameState(),
        getFollowingMonsters(),
        getActiveParty(),
        isPartyReady()
      ]);

      // Check for API errors
      if (!gameStateResponse.success) {
        throw new Error(gameStateResponse.error || 'Failed to load game state');
      }

      if (!followingResponse.success) {
        throw new Error(followingResponse.error || 'Failed to load following monsters');
      }

      // Update state with API responses
      setGameState(gameStateResponse.game_state);
      setFollowingMonsters(followingResponse.following_monsters.details || []);
      setActiveParty(partyResponse.active_party?.details || []);
      setPartyReady(readyResponse.ready_for_dungeon || false);

      console.log('✅ Home Base Data Loaded:', {
        gameStatus: gameStateResponse.game_state.game_status,
        followingCount: followingResponse.following_monsters.count,
        partyCount: partyResponse.active_party?.count || 0,
        readyForDungeon: readyResponse.ready_for_dungeon
      });

    } catch (err) {
      console.error('❌ Failed to load home base data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle party toggle (add/remove monster)
   */
  const handlePartyToggle = async (monster, isInParty) => {
    if (isInParty) {
      await removeFromParty(monster, activeParty);
    } else {
      await addToParty(monster, activeParty);
    }
  };

  /**
   * Check if monster is in active party
   */
  const isMonsterInParty = (monster) => {
    return activeParty.some(partyMonster => partyMonster.id === monster.id);
  };

  /**
   * Handle entering dungeon
   */
  const handleEnterDungeon = async () => {
    if (!partyReady) {
      alert('Add monsters to your party before entering the dungeon!');
      return;
    }

    if (onEnterDungeon) {
      onEnterDungeon();
    }
  };

  /**
   * Get paginated following monsters
   */
  const getPaginatedMonsters = () => {
    const startIndex = (currentPage - 1) * monstersPerPage;
    const endIndex = startIndex + monstersPerPage;
    return followingMonsters.slice(startIndex, endIndex);
  };

  /**
   * Calculate pagination info
   */
  const totalPages = Math.ceil(followingMonsters.length / monstersPerPage);
  const paginatedMonsters = getPaginatedMonsters();

  // Loading state
  if (loading) {
    return (
      <div className="homebase-screen">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="loading-text">Loading your home base...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="homebase-screen">
        <div className="error-container">
          <h2>❌ Error Loading Home Base</h2>
          <p>{error}</p>
          <button onClick={loadHomeBaseData} className="btn btn-primary">
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="homebase-screen">
      {/* Home Base Header */}
      <header className="homebase-header">
        <h1>🏠 Home Base</h1>
        <p>Prepare your party and venture into the unknown dungeons</p>
      </header>

      {/* Active Party Section - Top */}
      <section className="active-party-section">
        <div className="section-header">
          <h2>⚔️ Active Party ({activeParty.length}/4)</h2>
          <div className="party-status">
            {partyReady ? (
              <span className="status-badge status-success">✅ Ready for Dungeon</span>
            ) : (
              <span className="status-badge status-pending">⏳ Add Monsters to Party</span>
            )}
          </div>
        </div>

        <div className="active-party-container">
          {activeParty.length === 0 ? (
            <div className="empty-party">
              <div className="empty-party-content">
                <div className="empty-icon">👥</div>
                <h3>No Active Party</h3>
                <p>Click the <strong>+</strong> button on monsters below to add them to your party</p>
              </div>
            </div>
          ) : (
            <div className="party-grid">
              {activeParty.map(monster => (
                <div key={monster.id} className="party-monster-wrapper">
                  <MonsterCard
                    monster={monster}
                    size="small"
                    showPartyBadge={true}
                  />
                  <PartyToggleButton
                    monster={monster}
                    isInParty={true}
                    isPartyFull={false}
                    onToggle={handlePartyToggle}
                    disabled={updating}
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Enter Dungeon Button */}
        <div className="dungeon-actions">
          <button 
            onClick={handleEnterDungeon}
            disabled={!partyReady || updating}
            className={`btn btn-lg ${partyReady ? 'btn-primary' : 'btn-secondary'}`}
          >
            {updating ? '⏳ Updating Party...' : 
             partyReady ? '🏰 Enter Dungeon' : '⏳ Form Party First'}
          </button>
        </div>
      </section>

      {/* Following Monsters Section - Bottom */}
      <section className="following-monsters-section">
        <div className="section-header">
          <h2>📚 Your Monster Collection ({followingMonsters.length})</h2>
          {followingMonsters.length > monstersPerPage && (
            <div className="pagination-info">
              Page {currentPage} of {totalPages}
            </div>
          )}
        </div>

        {followingMonsters.length === 0 ? (
          <div className="empty-following">
            <div className="empty-following-content">
              <div className="empty-icon">🏛️</div>
              <h3>No Monsters in Collection</h3>
              <p>Visit the Monster Sanctuary to generate monsters and add them to your collection</p>
            </div>
          </div>
        ) : (
          <>
            {/* Monsters Grid */}
            <div className="following-monsters-grid">
              {paginatedMonsters.map(monster => (
                <div key={monster.id} className="following-monster-wrapper">
                  <MonsterCard
                    monster={monster}
                    size="normal"
                  />
                  <PartyToggleButton
                    monster={monster}
                    isInParty={isMonsterInParty(monster)}
                    isPartyFull={activeParty.length >= 4}
                    onToggle={handlePartyToggle}
                    disabled={updating}
                  />
                </div>
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="pagination-controls">
                <button 
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                  className="btn btn-secondary btn-sm"
                >
                  ⏮️ First
                </button>
                <button 
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="btn btn-secondary btn-sm"
                >
                  ⬅️ Previous
                </button>
                
                <span className="page-indicator">
                  {currentPage} / {totalPages}
                </span>
                
                <button 
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="btn btn-secondary btn-sm"
                >
                  Next ➡️
                </button>
                <button 
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage === totalPages}
                  className="btn btn-secondary btn-sm"
                >
                  Last ⏭️
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}

export default HomeBaseScreen;