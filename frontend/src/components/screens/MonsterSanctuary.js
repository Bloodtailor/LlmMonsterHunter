// Monster Sanctuary Screen - CLEANED UP WITH PAGINATION
// Displays all monsters as flippable cards in a beautiful sanctuary layout
// Now includes pagination controls and unfiltered statistics

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

// Helper function to calculate sanctuary stats (UNFILTERED)
function calculateSanctuaryStats(allMonsters) {
  return {
    total: allMonsters.length,
    totalAbilities: allMonsters.reduce((sum, monster) => sum + monster.ability_count, 0),
    withArt: allMonsters.filter(monster => monster.card_art?.exists).length,
    uniqueSpecies: new Set(allMonsters.map(monster => monster.species)).size
  };
}

// Helper function to paginate results
function paginateMonsters(monsters, pageSize, currentPage) {
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedMonsters = monsters.slice(startIndex, endIndex);
  
  return {
    monsters: paginatedMonsters,
    totalPages: Math.ceil(monsters.length / pageSize),
    currentPage,
    pageSize,
    totalItems: monsters.length,
    startIndex: startIndex + 1,
    endIndex: Math.min(endIndex, monsters.length)
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

// Pagination Controls Component
function PaginationControls({ pagination, onPageChange, onPageSizeChange }) {
  const { currentPage, totalPages, pageSize, totalItems, startIndex, endIndex } = pagination;
  
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const start = Math.max(1, currentPage - 2);
      const end = Math.min(totalPages, start + maxVisiblePages - 1);
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
    }
    
    return pages;
  };
  
  if (totalPages <= 1) return null;
  
  return (
    <div className="pagination-controls">
      <div className="pagination-info">
        <span>Showing {startIndex}-{endIndex} of {totalItems} monsters</span>
        <select 
          value={pageSize} 
          onChange={(e) => onPageSizeChange(parseInt(e.target.value))}
          className="page-size-select"
        >
          <option value="6">6 per page</option>
          <option value="12">12 per page</option>
          <option value="24">24 per page</option>
          <option value="48">48 per page</option>
        </select>
      </div>
      
      <div className="pagination-buttons">
        <button 
          onClick={() => onPageChange(1)}
          disabled={currentPage === 1}
          className="btn btn-secondary btn-sm"
        >
          ⏮️ First
        </button>
        <button 
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="btn btn-secondary btn-sm"
        >
          ⬅️ Prev
        </button>
        
        {getPageNumbers().map(pageNum => (
          <button
            key={pageNum}
            onClick={() => onPageChange(pageNum)}
            className={`btn btn-sm ${pageNum === currentPage ? 'btn-primary' : 'btn-secondary'}`}
          >
            {pageNum}
          </button>
        ))}
        
        <button 
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="btn btn-secondary btn-sm"
        >
          Next ➡️
        </button>
        <button 
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage === totalPages}
          className="btn btn-secondary btn-sm"
        >
          Last ⏭️
        </button>
      </div>
    </div>
  );
}

function MonsterSanctuary({ gameData }) {
  const [monsters, setMonsters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatingMonster, setGeneratingMonster] = useState(false);
  const [sortBy, setSortBy] = useState('newest');
  const [filterBy, setFilterBy] = useState('all');
  const [cardSize, setCardSize] = useState('normal');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);

  // Load monsters on component mount
  useEffect(() => {
    loadMonsters();
  }, []);
  
  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [sortBy, filterBy]);

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

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    // Scroll to top of monster gallery
    document.querySelector('.monster-gallery')?.scrollIntoView({ behavior: 'smooth' });
  };

  const handlePageSizeChange = (newPageSize) => {
    setPageSize(newPageSize);
    setCurrentPage(1); // Reset to first page
  };

  // Get filtered and sorted monsters
  const filteredMonsters = getFilteredAndSortedMonsters(monsters, sortBy, filterBy);
  
  // Apply pagination
  const pagination = paginateMonsters(filteredMonsters, pageSize, currentPage);
  const displayedMonsters = pagination.monsters;
  
  // Calculate stats from ALL monsters (unfiltered)
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

      {/* Pagination Controls (Top) */}
      {filteredMonsters.length > 0 && (
        <PaginationControls 
          pagination={pagination}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
        />
      )}

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
            {displayedMonsters.map(monster => (
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

      {/* Pagination Controls (Bottom) */}
      {filteredMonsters.length > 0 && (
        <PaginationControls 
          pagination={pagination}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
        />
      )}

      {/* Sanctuary Stats - NOW REFLECTS ALL MONSTERS (UNFILTERED) */}
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