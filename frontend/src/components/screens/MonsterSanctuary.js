// Monster Sanctuary Screen - ENHANCED WITH SERVER-SIDE PAGINATION
// Now uses the enhanced backend API with server-side filtering, sorting, and pagination
// Removed client-side processing for better performance and scalability

import React, { useState, useEffect } from 'react';
import MonsterCard from '../game/MonsterCard';

// API call helper with enhanced error handling
async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  return await response.json();
}

// Load monsters using the enhanced API with server-side pagination
async function loadMonsters({ limit, offset, filter, sort }) {
  try {
    // Build query parameters for the enhanced API
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit);
    if (offset) params.append('offset', offset);
    if (filter && filter !== 'all') params.append('filter', filter);
    if (sort) params.append('sort', sort);
    
    const url = `http://localhost:5000/api/monsters?${params.toString()}`;
    const response = await apiRequest(url);
    
    if (response.success) {
      return {
        monsters: response.monsters || [],
        total: response.total || 0,
        count: response.count || 0,
        pagination: response.pagination || {},
        filtersApplied: response.filters_applied || {}
      };
    } else {
      throw new Error(response.error || 'Failed to load monsters');
    }
  } catch (error) {
    console.error('Error loading monsters:', error);
    throw error;
  }
}

// Load sanctuary statistics using the enhanced stats API
async function loadSanctuaryStats(filter = 'all') {
  try {
    const params = new URLSearchParams();
    if (filter && filter !== 'all') params.append('filter', filter);
    
    const url = `http://localhost:5000/api/monsters/stats?${params.toString()}`;
    const response = await apiRequest(url);
    
    if (response.success) {
      return {
        stats: response.stats,
        filterApplied: response.filter_applied,
        context: response.context // Overall stats when filtering is applied
      };
    } else {
      throw new Error(response.error || 'Failed to load stats');
    }
  } catch (error) {
    console.error('Error loading stats:', error);
    throw error;
  }
}

// Pagination Controls Component - Enhanced for server-side pagination
function PaginationControls({ 
  monsters, 
  total, 
  currentPage, 
  pageSize, 
  onPageChange, 
  onPageSizeChange,
  loading 
}) {
  const totalPages = Math.ceil(total / pageSize);
  const startIndex = (currentPage - 1) * pageSize + 1;
  const endIndex = Math.min(currentPage * pageSize, total);
  
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
  
  if (total <= pageSize) return null;
  
  return (
    <div className="pagination-controls">
      <div className="pagination-info">
        <span>
          {loading ? 'Loading...' : `Showing ${startIndex}-${endIndex} of ${total} monsters`}
        </span>
        <select 
          value={pageSize} 
          onChange={(e) => onPageSizeChange(parseInt(e.target.value))}
          className="page-size-select"
          disabled={loading}
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
          disabled={currentPage === 1 || loading}
          className="btn btn-secondary btn-sm"
        >
          ⏮️ First
        </button>
        <button 
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1 || loading}
          className="btn btn-secondary btn-sm"
        >
          ⬅️ Prev
        </button>
        
        {getPageNumbers().map(pageNum => (
          <button
            key={pageNum}
            onClick={() => onPageChange(pageNum)}
            disabled={loading}
            className={`btn btn-sm ${pageNum === currentPage ? 'btn-primary' : 'btn-secondary'}`}
          >
            {pageNum}
          </button>
        ))}
        
        <button 
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages || loading}
          className="btn btn-secondary btn-sm"
        >
          Next ➡️
        </button>
        <button 
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage === totalPages || loading}
          className="btn btn-secondary btn-sm"
        >
          Last ⏭️
        </button>
      </div>
    </div>
  );
}

// Sanctuary Stats Component - Enhanced to show filtered vs overall stats
function SanctuaryStats({ stats, filterApplied, context, loading }) {
  if (loading) {
    return (
      <section className="sanctuary-stats">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="loading-text">Loading sanctuary statistics...</p>
        </div>
      </section>
    );
  }

  if (!stats) return null;

  return (
    <section className="sanctuary-stats">
      <h3>📊 Sanctuary Statistics</h3>
      
      {/* Show filter context if filtering is applied */}
      {filterApplied && filterApplied !== 'all' && context && (
        <div className="alert alert-info mb-lg">
          <p>
            <strong>📋 Current View:</strong> Showing stats for monsters {filterApplied.replace('_', ' ')}.
          </p>
          <p>
            <strong>🏛️ Total Sanctuary:</strong> {context.all_monsters_count} total monsters, 
            {context.all_monsters_with_art} with card art 
            ({context.overall_card_art_percentage}% overall).
          </p>
        </div>
      )}
      
      <div className="grid-auto-fit grid-auto-fit-sm">
        <div className="stat-card">
          <span className="stat-number">{stats.total_monsters}</span>
          <span className="stat-label">
            {filterApplied && filterApplied !== 'all' ? 
              `${filterApplied.replace('_', ' ')}` : 
              'Total Monsters'
            }
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{stats.total_abilities}</span>
          <span className="stat-label">Total Abilities</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{stats.with_card_art}</span>
          <span className="stat-label">With Card Art</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{stats.unique_species}</span>
          <span className="stat-label">Unique Species</span>
        </div>
      </div>
      
      {/* Show additional stats */}
      {stats.avg_abilities_per_monster && (
        <div className="mt-lg">
          <p className="text-center text-medium">
            <strong>Average Abilities per Monster:</strong> {stats.avg_abilities_per_monster.toFixed(1)} | 
            <strong> Card Art Coverage:</strong> {stats.card_art_percentage?.toFixed(1)}%
          </p>
        </div>
      )}
    </section>
  );
}

// Main Monster Sanctuary Component
function MonsterSanctuary({ gameData }) {
  // Core data state
  const [monsters, setMonsters] = useState([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState(null);
  const [statsContext, setStatsContext] = useState(null);
  
  // Loading and error states
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatingMonster, setGeneratingMonster] = useState(false);
  
  // Filter and pagination state
  const [sortBy, setSortBy] = useState('newest');
  const [filterBy, setFilterBy] = useState('all');
  const [cardSize, setCardSize] = useState('normal');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);

  // Load monsters whenever pagination or filter parameters change
  useEffect(() => {
    loadMonstersData();
  }, [currentPage, pageSize, sortBy, filterBy]);

  // Load stats whenever filter changes
  useEffect(() => {
    loadStatsData();
  }, [filterBy]);

  // Reset to page 1 when filters change
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1);
    }
  }, [sortBy, filterBy]);

  const loadMonstersData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const offset = (currentPage - 1) * pageSize;
      const data = await loadMonsters({
        limit: pageSize,
        offset: offset,
        filter: filterBy,
        sort: sortBy
      });
      
      setMonsters(data.monsters);
      setTotal(data.total);
      
      console.log(`✅ Loaded ${data.count} monsters (${data.total} total) with filters:`, data.filtersApplied);
      
    } catch (err) {
      setError('Cannot connect to backend server or failed to load monsters');
      console.error('Failed to load monsters:', err);
    }
    
    setLoading(false);
  };

  const loadStatsData = async () => {
    setStatsLoading(true);
    
    try {
      const data = await loadSanctuaryStats(filterBy);
      setStats(data.stats);
      setStatsContext(data.context);
      
      console.log(`📊 Loaded stats for filter '${data.filterApplied}':`, data.stats);
      
    } catch (err) {
      console.error('Failed to load stats:', err);
      // Don't set error for stats - just log it
    }
    
    setStatsLoading(false);
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
        // Reload the first page to see the new monster
        setCurrentPage(1);
        await loadMonstersData();
        await loadStatsData();
        
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
        // Reload current page to get updated abilities
        await loadMonstersData();
        await loadStatsData();
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

  const handleSortChange = (newSort) => {
    setSortBy(newSort);
    // currentPage will reset to 1 via useEffect
  };

  const handleFilterChange = (newFilter) => {
    setFilterBy(newFilter);
    // currentPage will reset to 1 via useEffect
  };

  // Initial loading state
  if (loading && monsters.length === 0) {
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
          <button onClick={loadMonstersData} className="btn btn-secondary mt-md">
            🔄 Retry
          </button>
        </div>
      )}

      {/* Sanctuary Controls */}
      <section className="sanctuary-controls">
        <div className="monster-count">
          <span className="count-badge">
            {loading ? '...' : `${total} monsters`}
          </span>
          {filterBy !== 'all' && (
            <span className="filter-info">
              (filtered: {filterBy.replace('_', ' ')})
            </span>
          )}
        </div>
        
        <div className="controls-group">
          <div className="control-group">
            <label htmlFor="sort-select">Sort by:</label>
            <select 
              id="sort-select"
              value={sortBy} 
              onChange={(e) => handleSortChange(e.target.value)}
              className="sanctuary-select"
              disabled={loading}
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
              onChange={(e) => handleFilterChange(e.target.value)}
              className="sanctuary-select"
              disabled={loading}
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
      <PaginationControls 
        monsters={monsters}
        total={total}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        loading={loading}
      />

      {/* Monster Gallery */}
      <section className="monster-gallery">
        {total === 0 && !loading ? (
          <div className="empty-sanctuary">
            <div className="empty-content">
              <div className="empty-icon">🏛️</div>
              <h3>Your Sanctuary Awaits</h3>
              {filterBy === 'all' ? (
                <>
                  <p>No monsters have been summoned yet.</p>
                  <p>Create your first monster to begin building your legendary collection!</p>
                </>
              ) : (
                <>
                  <p>No monsters match your current filter: "{filterBy.replace('_', ' ')}"</p>
                  <p>Try changing the filter or summon more monsters!</p>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className={`monster-cards-grid ${cardSize}-cards`}>
            {loading ? (
              // Show loading placeholders
              Array.from({ length: Math.min(pageSize, 6) }).map((_, index) => (
                <div key={index} className="card">
                  <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p className="loading-text">Loading monster...</p>
                  </div>
                </div>
              ))
            ) : (
              monsters.map(monster => (
                <MonsterCard
                  key={monster.id}
                  monster={monster}
                  size={cardSize}
                  onAbilityGenerate={handleAbilityGenerate}
                />
              ))
            )}
          </div>
        )}
      </section>

      {/* Pagination Controls (Bottom) */}
      {total > pageSize && (
        <PaginationControls 
          monsters={monsters}
          total={total}
          currentPage={currentPage}
          pageSize={pageSize}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          loading={loading}
        />
      )}

      {/* Sanctuary Stats - Shows filtered or overall stats */}
      <SanctuaryStats 
        stats={stats}
        filterApplied={filterBy}
        context={statsContext}
        loading={statsLoading}
      />
    </div>
  );
}

export default MonsterSanctuary;