// Monster Sanctuary Screen - ENHANCED WITH FLIPPABLE CARDS
// Displays all monsters as flippable cards in a beautiful sanctuary layout
// Replaces the old GameHomeBase screen

import React, { useState, useEffect } from 'react';
import MonsterCard from '../game/MonsterCard';

function MonsterSanctuary({ gameData }) {
  const [monsters, setMonsters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatingMonster, setGeneratingMonster] = useState(false);
  const [sortBy, setSortBy] = useState('newest'); // 'newest', 'oldest', 'name', 'species'
  const [filterBy, setFilterBy] = useState('all'); // 'all', 'with_art', 'without_art'
  const [cardSize, setCardSize] = useState('normal'); // 'small', 'normal', 'large'

  // Load monsters on component mount
  useEffect(() => {
    loadMonsters();
  }, []);

  const loadMonsters = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/monsters');
      const data = await response.json();
      
      if (data.success) {
        setMonsters(data.monsters);
      } else {
        setError(data.error || 'Failed to load monsters');
      }
    } catch (err) {
      setError('Cannot connect to backend server');
      console.error('Failed to load monsters:', err);
    }
    
    setLoading(false);
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
          prompt_name: 'detailed_monster',
          generate_card_art: true
        })
      });
      
      const result = await response.json();
      
      if (result.success && result.monster) {
        // Add new monster to the beginning of the list
        setMonsters(prev => [result.monster, ...prev]);
        
        console.log(`✅ Generated ${result.monster.name} with ${result.monster.ability_count} abilities!`);
        if (result.monster.card_art?.exists) {
          console.log(`🎨 Card art generated: ${result.monster.card_art.relative_path}`);
        }
      } else {
        setError(result.error || 'Monster generation failed');
      }
    } catch (err) {
      setError('Error generating monster');
      console.error('Error generating monster:', err);
    }
    
    setGeneratingMonster(false);
  };

  const handleAbilityGenerate = async (monsterId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/monsters/${monsterId}/abilities`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wait_for_completion: true
        })
      });
      
      const result = await response.json();
      
      if (result.success && result.ability) {
        // Reload monsters to get updated abilities
        await loadMonsters();
        console.log(`✅ Generated ability "${result.ability.name}" for monster ${monsterId}!`);
      } else {
        console.error('Ability generation failed:', result.error);
      }
    } catch (err) {
      console.error('Error generating ability:', err);
    }
  };

  // Filter and sort monsters
  const getFilteredAndSortedMonsters = () => {
    let filtered = [...monsters];
    
    // Apply filters
    if (filterBy === 'with_art') {
      filtered = filtered.filter(monster => monster.card_art?.exists);
    } else if (filterBy === 'without_art') {
      filtered = filtered.filter(monster => !monster.card_art?.exists);
    }
    
    // Apply sorting
    switch (sortBy) {
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        break;
      case 'name':
        filtered.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'species':
        filtered.sort((a, b) => a.species.localeCompare(b.species));
        break;
      case 'newest':
      default:
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
    }
    
    return filtered;
  };

  const filteredMonsters = getFilteredAndSortedMonsters();

  if (loading) {
    return (
      <div className="monster-sanctuary">
        <div className="sanctuary-loading">
          <div className="loading-spinner"></div>
          <p>Loading your Monster Sanctuary...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="monster-sanctuary">
      {/* Sanctuary Header */}
      <section className="sanctuary-header">
        <div className="header-content">
          <h1>🏛️ Monster Sanctuary</h1>
          <p>Welcome to your mystical sanctuary where legendary creatures await your discovery. Each monster is unique with its own personality, abilities, and backstory.</p>
          
          {gameData?.features?.monster_generation ? (
            <div className="quick-actions">
              <button 
                onClick={generateNewMonster}
                disabled={generatingMonster}
                className="primary-action-button"
              >
                {generatingMonster ? '🔄 Summoning Monster...' : '✨ Summon New Monster'}
              </button>
            </div>
          ) : (
            <div className="feature-notice">
              <p>🔧 Monster summoning system is currently being prepared...</p>
            </div>
          )}
        </div>
      </section>

      {/* Error Display */}
      {error && (
        <section className="error-section">
          <div className="error-message">
            <h3>❌ Error</h3>
            <p>{error}</p>
            <button onClick={loadMonsters} className="retry-button">
              🔄 Retry
            </button>
          </div>
        </section>
      )}

      {/* Sanctuary Controls */}
      <section className="sanctuary-controls">
        <div className="monster-count">
          <span className="count-badge">{filteredMonsters.length} monsters</span>
          {filteredMonsters.length !== monsters.length && (
            <span className="filter-info">({monsters.length} total)</span>
          )}
        </div>
        
        <div className="controls-group">
          <div className="control-group">
            <label htmlFor="sort-select">Sort by:</label>
            <select 
              id="sort-select"
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="sanctuary-select"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="name">Name A-Z</option>
              <option value="species">Species</option>
            </select>
          </div>
          
          <div className="control-group">
            <label htmlFor="filter-select">Filter:</label>
            <select 
              id="filter-select"
              value={filterBy} 
              onChange={(e) => setFilterBy(e.target.value)}
              className="sanctuary-select"
            >
              <option value="all">All Monsters</option>
              <option value="with_art">With Card Art</option>
              <option value="without_art">Without Card Art</option>
            </select>
          </div>
          
          <div className="control-group">
            <label htmlFor="size-select">Card Size:</label>
            <select 
              id="size-select"
              value={cardSize} 
              onChange={(e) => setCardSize(e.target.value)}
              className="sanctuary-select"
            >
              <option value="small">Small</option>
              <option value="normal">Normal</option>
              <option value="large">Large</option>
            </select>
          </div>
        </div>
      </section>

      {/* Monster Gallery */}
      <section className="monster-gallery">
        {filteredMonsters.length === 0 ? (
          <div className="empty-sanctuary">
            <div className="empty-content">
              <div className="empty-icon">🏛️</div>
              <h3>Your Sanctuary Awaits</h3>
              {monsters.length === 0 ? (
                <>
                  <p>No monsters have been summoned yet.</p>
                  <p>Create your first monster to begin building your legendary collection!</p>
                </>
              ) : (
                <>
                  <p>No monsters match your current filters.</p>
                  <p>Try adjusting the sort and filter options above.</p>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className={`monster-cards-grid ${cardSize}-cards`}>
            {filteredMonsters.map(monster => (
              <MonsterCard
                key={monster.id}
                monster={monster}
                size={cardSize}
                onAbilityGenerate={handleAbilityGenerate}
              />
            ))}
          </div>
        )}
      </section>

      {/* Sanctuary Stats */}
      {monsters.length > 0 && (
        <section className="sanctuary-stats">
          <h3>📊 Sanctuary Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-number">{monsters.length}</span>
              <span className="stat-label">Total Monsters</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">
                {monsters.reduce((sum, monster) => sum + monster.ability_count, 0)}
              </span>
              <span className="stat-label">Total Abilities</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">
                {monsters.filter(monster => monster.card_art?.exists).length}
              </span>
              <span className="stat-label">With Card Art</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">
                {new Set(monsters.map(monster => monster.species)).size}
              </span>
              <span className="stat-label">Unique Species</span>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default MonsterSanctuary;