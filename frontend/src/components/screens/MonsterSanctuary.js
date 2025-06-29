// Monster Sanctuary Screen - CLEANED UP
// Displays all monsters as flippable cards in a beautiful sanctuary layout

import React, { useState, useEffect } from 'react';
import MonsterCard from '../game/MonsterCard';

// Helper function for filtering and sorting monsters
function getFilteredAndSortedMonsters(monsters, sortBy, filterBy) {
  let filtered = [...monsters];
  
  // Apply filters
  if (filterBy === 'with_art') {
    filtered = filtered.filter(monster => monster.card_art?.exists);
  } else if (filterBy === 'without_art') {
    filtered = filtered.filter(monster => !monster.card_art?.exists);
  }
  
  // Apply sorting
  const sortFunctions = {
    oldest: (a, b) => new Date(a.created_at) - new Date(b.created_at),
    name: (a, b) => a.name.localeCompare(b.name),
    species: (a, b) => a.species.localeCompare(b.species),
    newest: (a, b) => new Date(b.created_at) - new Date(a.created_at)
  };
  
  return filtered.sort(sortFunctions[sortBy] || sortFunctions.newest);
}

// Helper function to calculate sanctuary stats
function calculateSanctuaryStats(monsters) {
  return {
    total: monsters.length,
    totalAbilities: monsters.reduce((sum, monster) => sum + monster.ability_count, 0),
    withArt: monsters.filter(monster => monster.card_art?.exists).length,
    uniqueSpecies: new Set(monsters.map(monster => monster.species)).size
  };
}

// API call helper
async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  return await response.json();
}

function MonsterSanctuary({ gameData }) {
  const [monsters, setMonsters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatingMonster, setGeneratingMonster] = useState(false);
  const [sortBy, setSortBy] = useState('newest');
  const [filterBy, setFilterBy] = useState('all');
  const [cardSize, setCardSize] = useState('normal');

  // Load monsters on component mount
  useEffect(() => {
    loadMonsters();
  }, []);

  const loadMonsters = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiRequest('http://localhost:5000/api/monsters');
      
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
      const result = await apiRequest('http://localhost:5000/api/monsters/generate', {
        method: 'POST',
        body: JSON.stringify({
          prompt_name: 'detailed_monster',
          generate_card_art: true
        })
      });
      
      if (result.success && result.monster) {
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
      const result = await apiRequest(`http://localhost:5000/api/monsters/${monsterId}/abilities`, {
        method: 'POST',
        body: JSON.stringify({ wait_for_completion: true })
      });
      
      if (result.success && result.ability) {
        await loadMonsters(); // Reload to get updated abilities
        console.log(`✅ Generated ability "${result.ability.name}" for monster ${monsterId}!`);
      } else {
        console.error('Ability generation failed:', result.error);
      }
    } catch (err) {
      console.error('Error generating ability:', err);
    }
  };

  // Get filtered and sorted monsters
  const filteredMonsters = getFilteredAndSortedMonsters(monsters, sortBy, filterBy);
  const stats = calculateSanctuaryStats(monsters);

  if (loading) {
    return (
      <div className="monster-sanctuary">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="loading-text">Loading your Monster Sanctuary...</p>
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
                className="btn btn-secondary btn-lg btn-hover-lift"
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
        <div className="alert alert-error">
          <h3>❌ Error</h3>
          <p>{error}</p>
          <button onClick={loadMonsters} className="btn btn-secondary mt-md">
            🔄 Retry
          </button>
        </div>
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
          <div className="grid-auto-fit grid-auto-fit-sm">
            <div className="stat-card">
              <span className="stat-number">{stats.total}</span>
              <span className="stat-label">Total Monsters</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">{stats.totalAbilities}</span>
              <span className="stat-label">Total Abilities</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">{stats.withArt}</span>
              <span className="stat-label">With Card Art</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">{stats.uniqueSpecies}</span>
              <span className="stat-label">Unique Species</span>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default MonsterSanctuary;