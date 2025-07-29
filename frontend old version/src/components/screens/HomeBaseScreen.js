// Home Base Screen - WITH REUSABLE PARTY DISPLAY
// Displays following monsters and active party using the reusable PartyDisplay component
// Monsters in party are hidden from the pool automatically

import React, { useState, useEffect } from 'react';
import MonsterCard from '../game/MonsterCard';
import PartyDisplay from '../game/PartyDisplay';
import { usePartyManager } from '../game/PartyManager';
import { getGameState, getFollowingMonsters, getActiveParty, isPartyReady } from '../../services/gameStateApi';
import { 
  getAvailablePoolMonsters, 
  isMonsterInParty, 
  getPaginatedMonsters, 
  validatePartySize 
} from '../../utils/helpers';

function HomeBaseScreen({ onEnterDungeon }) {
  // State management
  const [gameState, setGameState] = useState(null);
  const [followingMonsters, setFollowingMonsters] = useState([]);
  const [activeParty, setActiveParty] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [partyReady, setPartyReady] = useState(false);

  // Pagination state for pool monsters
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

  // Reset to first page when party changes (affects available pool)
  useEffect(() => {
    setCurrentPage(1);
  }, [activeParty.length]);

  /**
   * Load all home base data from APIs
   */
  const loadHomeBaseData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [gameStateResponse, followingResponse, partyResponse, readyResponse] = await Promise.all([
        getGameState(),
        getFollowingMonsters(),
        getActiveParty(),
        isPartyReady()
      ]);

      if (!gameStateResponse.success) {
        throw new Error(gameStateResponse.error || 'Failed to load game state');
      }

      if (!followingResponse.success) {
        throw new Error(followingResponse.error || 'Failed to load following monsters');
      }

      setGameState(gameStateResponse.game_state);
      setFollowingMonsters(followingResponse.following_monsters.details || []);
      setActiveParty(partyResponse.active_party?.details || []);
      setPartyReady(readyResponse.ready_for_dungeon || false);

      console.log('✅ Home Base Data Loaded:', {
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
  const handlePartyToggle = async (monster, isInPartyBool) => {
    if (isInPartyBool) {
      await removeFromParty(monster, activeParty);
    } else {
      await addToParty(monster, activeParty);
    }
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

  // Calculate filtered and paginated data using utilities
  const availablePoolMonsters = getAvailablePoolMonsters(followingMonsters, activeParty);
  const paginationInfo = getPaginatedMonsters(availablePoolMonsters, currentPage, monstersPerPage);
  const partyValidation = validatePartySize(activeParty);

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

      {/* Active Party Section - Using Reusable Component */}
      <PartyDisplay
        partyMonsters={activeParty}
        title="⚔️ Active Party"
        showHeader={true}
        showPartyToggles={true}
        showActions={true}
        emptyTitle="No Active Party"
        emptyMessage="Click the + button on monsters below to add them to your party"
        emptyIcon="👥"
        onPartyToggle={handlePartyToggle}
        onActionClick={handleEnterDungeon}
        partyReady={partyReady}
        updating={updating}
        maxPartySize={4}
      />

      {/* Available Pool Section */}
      <section className="following-monsters-section">
        <div className="section-header">
          <h2>📚 Available Monsters ({availablePoolMonsters.length} available of {followingMonsters.length} total)</h2>
          {paginationInfo.totalPages > 1 && (
            <div className="pagination-info">
              Showing {paginationInfo.startIndex}-{paginationInfo.endIndex} of {paginationInfo.totalItems}
            </div>
          )}
        </div>

        {availablePoolMonsters.length === 0 ? (
          <div className="empty-following">
            <div className="empty-following-content">
              <div className="empty-icon">
                {followingMonsters.length === 0 ? '🏛️' : '✅'}
              </div>
              <h3>
                {followingMonsters.length === 0 ? 'No Monsters in Collection' : 'All Monsters in Party!'}
              </h3>
              <p>
                {followingMonsters.length === 0 
                  ? 'Visit the Monster Sanctuary to generate monsters and add them to your collection'
                  : 'All your monsters are currently in your active party. Remove some to see them here.'
                }
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Available Monsters Grid */}
            <div className="following-monsters-grid">
              {paginationInfo.items.map(monster => (
                <div key={monster.id} className="following-monster-wrapper">
                  <MonsterCard
                    monster={monster}
                    size="normal"
                    showPartyToggle={true}
                    isInParty={false} // These are filtered to NOT be in party
                    isPartyFull={partyValidation.isFull}
                    onPartyToggle={handlePartyToggle}
                    partyDisabled={updating}
                  />
                </div>
              ))}
            </div>

            {/* Pagination Controls */}
            {paginationInfo.totalPages > 1 && (
              <div className="pagination-controls">
                <button 
                  onClick={() => setCurrentPage(1)}
                  disabled={!paginationInfo.hasPrevious}
                  className="btn btn-secondary btn-sm"
                >
                  ⏮️ First
                </button>
                <button 
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={!paginationInfo.hasPrevious}
                  className="btn btn-secondary btn-sm"
                >
                  ⬅️ Previous
                </button>
                
                <span className="page-indicator">
                  {paginationInfo.currentPage} / {paginationInfo.totalPages}
                </span>
                
                <button 
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={!paginationInfo.hasNext}
                  className="btn btn-secondary btn-sm"
                >
                  Next ➡️
                </button>
                <button 
                  onClick={() => setCurrentPage(paginationInfo.totalPages)}
                  disabled={!paginationInfo.hasNext}
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