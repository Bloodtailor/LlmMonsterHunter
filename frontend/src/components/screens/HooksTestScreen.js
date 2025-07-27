// Hooks Test Screen - Test the new monster hooks with clean transformed data
// Shows side-by-side comparison of loading states, errors, and clean game objects
// Perfect for verifying the hook architecture works correctly

// Example: How components use the updated monster hooks
// Shows the new pattern where components control when API calls happen

import React, { useState, useEffect, useCallback } from 'react';
import {
  useMonsterCollection,
  useMonster,
  useMonsterStats,
  useMonsterGeneration
} from '../../refactored/app/hooks/useMonsters.js';

function HooksTestScreen() {
  // UI state managed by component
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('newest');
  const [limit] = useState(12);

  // Hook provides data access and pagination state
  const {
    monsters,
    pagination,
    isLoading,
    currentPage,
    loadMonsters,
    goToPage
  } = useMonsterCollection();

  // Component controls when to load based on dependencies
  useEffect(() => {
    console.log('🔄 Loading monsters due to filter/sort change');
    loadMonsters({ filter, sort, limit });
  }, [filter, sort, limit, loadMonsters]);

  // Component controls pagination
  const handlePageChange = useCallback((page) => {
    goToPage(page, limit);
    // Load monsters with current filters after page change
    loadMonsters({ filter, sort, limit });
  }, [filter, sort, limit, loadMonsters, goToPage]);

  return (
    <div>
      {/* Filter Controls */}
      <div>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All Monsters</option>
          <option value="with_art">With Card Art</option>
          <option value="without_art">Without Card Art</option>
        </select>
        
        <select value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="name">By Name</option>
        </select>
      </div>

      {/* Monster Grid */}
      {isLoading ? (
        <div>Loading monsters...</div>
      ) : (
        <div>
          {monsters.map(monster => (
            <div key={monster.id}>
              <h3>{monster.name}</h3>
              <p>{monster.species}</p>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {pagination && (
        <div>
          <button 
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={!pagination.hasPrevPage}
          >
            Previous
          </button>
          <span>Page {currentPage} of {pagination.totalPages}</span>
          <button 
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={!pagination.hasNextPage}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default HooksTestScreen;