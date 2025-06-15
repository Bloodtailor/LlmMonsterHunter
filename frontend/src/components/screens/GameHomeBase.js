// Game Home Base Screen Component
// This is the actual game interface where players manage monsters and prepare for adventures

import React, { useState, useEffect } from 'react';

function GameHomeBase({ gameData }) {
  const [monsters, setMonsters] = useState([]);
  const [generatingMonster, setGeneratingMonster] = useState(false);
  const [selectedMonster, setSelectedMonster] = useState(null);

  // Load player's monsters on component mount
  useEffect(() => {
    loadMonsters();
  }, []);

  const loadMonsters = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/monsters');
      const data = await response.json();
      
      if (data.success) {
        setMonsters(data.monsters);
      }
    } catch (error) {
      console.error('Failed to load monsters:', error);
    }
  };

  const generateNewMonster = async () => {
    setGeneratingMonster(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/monsters/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt_name: 'detailed_monster'
        })
      });
      
      const result = await response.json();
      
      if (result.success && result.monster) {
        // Add new monster to the list
        setMonsters(prev => [result.monster, ...prev]);
        setSelectedMonster(result.monster);
      } else {
        console.error('Monster generation failed:', result.error);
      }
    } catch (error) {
      console.error('Error generating monster:', error);
    }
    
    setGeneratingMonster(false);
  };

  const formatMonsterStats = (stats) => {
    return `HP: ${stats.max_health} | ATK: ${stats.attack} | DEF: ${stats.defense} | SPD: ${stats.speed}`;
  };

  return (
    <div className="game-homebase">
      {/* Welcome Header */}
      <section className="welcome-header">
        <div className="welcome-content">
          <h1>🏠 Welcome to Your Monster Sanctuary</h1>
          <p>This is your home base where you can manage your captured monsters, prepare for dungeon expeditions, and plan your next adventure.</p>
          
          {gameData?.features?.monster_generation ? (
            <div className="quick-actions">
              <button 
                onClick={generateNewMonster}
                disabled={generatingMonster}
                className="primary-action-button"
              >
                {generatingMonster ? '🔄 Generating Monster...' : '✨ Generate New Monster'}
              </button>
            </div>
          ) : (
            <div className="feature-notice">
              <p>🔧 Monster generation system is currently being prepared...</p>
            </div>
          )}
        </div>
      </section>

      {/* Monster Roster */}
      <section className="monster-roster">
        <div className="section-header">
          <h2>🐉 Your Monster Roster</h2>
          <span className="monster-count">{monsters.length} monsters</span>
        </div>
        
        {monsters.length === 0 ? (
          <div className="empty-roster">
            <div className="empty-content">
              <h3>📦 No monsters yet!</h3>
              <p>Generate your first monster to begin your adventure.</p>
              <p>Each monster is unique with its own personality, abilities, and backstory.</p>
            </div>
          </div>
        ) : (
          <div className="monster-grid">
            {monsters.map(monster => (
              <div 
                key={monster.id} 
                className={`monster-card ${selectedMonster?.id === monster.id ? 'selected' : ''}`}
                onClick={() => setSelectedMonster(selectedMonster?.id === monster.id ? null : monster)}
              >
                <div className="monster-card-header">
                  <h3>{monster.name}</h3>
                  <span className="monster-species">{monster.species}</span>
                </div>
                
                <div className="monster-description">
                  <p>{monster.description}</p>
                </div>
                
                <div className="monster-stats-summary">
                  <span className="stats-text">{formatMonsterStats(monster.stats)}</span>
                </div>
                
                {monster.personality_traits && monster.personality_traits.length > 0 && (
                  <div className="monster-traits">
                    {monster.personality_traits.slice(0, 2).map((trait, index) => (
                      <span key={index} className="trait-tag">{trait}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Monster Detail Panel */}
      {selectedMonster && (
        <section className="monster-detail">
          <div className="detail-header">
            <h2>🔍 {selectedMonster.name} Details</h2>
            <button 
              onClick={() => setSelectedMonster(null)}
              className="close-detail-button"
            >
              ✖️ Close
            </button>
          </div>
          
          <div className="detail-content">
            <div className="detail-section">
              <h3>📖 Backstory</h3>
              <p>{selectedMonster.backstory || 'This monster keeps its past mysterious...'}</p>
            </div>
            
            <div className="detail-section">
              <h3>📊 Complete Stats</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Health:</span>
                  <span className="stat-value">{selectedMonster.stats.current_health}/{selectedMonster.stats.max_health}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Attack:</span>
                  <span className="stat-value">{selectedMonster.stats.attack}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Defense:</span>
                  <span className="stat-value">{selectedMonster.stats.defense}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Speed:</span>
                  <span className="stat-value">{selectedMonster.stats.speed}</span>
                </div>
              </div>
            </div>
            
            {selectedMonster.personality_traits && selectedMonster.personality_traits.length > 0 && (
              <div className="detail-section">
                <h3>🎭 Personality Traits</h3>
                <div className="traits-list">
                  {selectedMonster.personality_traits.map((trait, index) => (
                    <span key={index} className="trait-tag large">{trait}</span>
                  ))}
                </div>
              </div>
            )}
            
            {selectedMonster.abilities && selectedMonster.abilities.length > 0 && (
              <div className="detail-section">
                <h3>⚡ Abilities</h3>
                <div className="abilities-list">
                  {selectedMonster.abilities.map((ability, index) => (
                    <div key={index} className="ability-item">
                      <h4>{ability.name}</h4>
                      <p>{ability.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Game Actions (Future Features) */}
      <section className="game-actions">
        <h2>🎯 Available Actions</h2>
        <div className="actions-grid">
          <div className="action-card disabled">
            <h3>🗺️ Enter Dungeon</h3>
            <p>Explore mysterious dungeons to find new monsters and treasures</p>
            <button disabled className="action-button">Coming Soon</button>
          </div>
          
          <div className="action-card disabled">
            <h3>💬 Chat with Monsters</h3>
            <p>Talk with your monsters to learn their stories and build relationships</p>
            <button disabled className="action-button">Coming Soon</button>
          </div>
          
          <div className="action-card disabled">
            <h3>⚔️ Battle Training</h3>
            <p>Train your monsters in combat to prepare for dungeon encounters</p>
            <button disabled className="action-button">Coming Soon</button>
          </div>
          
          <div className="action-card disabled">
            <h3>🎒 Manage Inventory</h3>
            <p>Organize items and equipment for your adventures</p>
            <button disabled className="action-button">Coming Soon</button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default GameHomeBase;