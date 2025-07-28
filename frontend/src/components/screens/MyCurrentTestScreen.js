// MyCurrentTestScreen - FOCUSED ARCHITECTURE TEST
// Tests our complete refactored architecture: useMonsterCollection + Full Pagination + MonsterCard
// Simple and focused - just pagination with monster cards

import React, { useState, useEffect, useCallback } from "react";
import { usePagination } from "../../refactored/shared/hooks/usePagination.js";
import { useMonsterCollection } from "../../refactored/app/hooks/useMonsters.js";
import FullPagination, { PAGINATION_LAYOUTS } from "../../refactored/shared/components/Pagination.js";
import { 
  Select,
  Alert,
  EmptyState,
  EMPTY_STATE_PRESETS
} from "../../refactored/shared/ui/index.js";

// Import our new MonsterCard (we'll need to adjust path when it's moved)
import MonsterCard from "../../refactored/components/cards/MonsterCard.js";// TODO: Update path to refactored version

function MyCurrentTestScreen() {
  // UI state
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('newest');
  const [limit, setLimit] = useState(12);
  const [cardSize, setCardSize] = useState('normal')

  // Domain hook - provides clean monster data
  const {
    rawResponse,
    monsters,
    total,
    isLoading,
    isError,
    error,
    loadMonsters
  } = useMonsterCollection();

  // Pagination hook
  const pagination = usePagination({ 
    limit, 
    total 
  });

  // Load monsters when filters or pagination changes
  const loadMonstersWithPagination = useCallback(() => {
    console.log('🔄 Loading monsters:', {
      filter,
      sort,
      limit,
      offset: pagination.currentOffset,
      page: pagination.currentPage
    });

    loadMonsters({
      limit,
      offset: pagination.currentOffset,
      filter: filter !== 'all' ? filter : undefined,
      sort
    });
  }, [filter, sort, limit, pagination.currentOffset, loadMonsters]);

  // Auto-load on mount and when dependencies change
  useEffect(() => {
    loadMonstersWithPagination();
  }, [loadMonstersWithPagination]);

  // Handle limit change (updates pagination)
  const handleLimitChange = useCallback((newLimit) => {
    setLimit(newLimit);
    pagination.firstPage();
  }, [pagination.firstPage]);

  // Handle filter/sort changes
  const handleFilterChange = useCallback((newFilter) => {
    setFilter(newFilter);
    pagination.firstPage(); // Reset to first page when filter changes
  }, [pagination.firstPage]);

  const handleSortChange = useCallback((newSort) => {
    setSort(newSort);
    pagination.firstPage(); // Reset to first page when sort changes
  }, [pagination.firstPage]);

  const handleCardSizeChange = useCallback((newCardSize) => {
    setCardSize(newCardSize);
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Header */}
      <div style={{ marginBottom: '30px', textAlign: 'center' }}>
        <h1>🧪 Monster Collection Architecture Test</h1>
        <p>Testing: useMonsterCollection + Full-Featured Pagination + Refactored MonsterCard</p>
      </div>

      {/* Controls */}
      <div style={{ 
        display: 'flex', 
        gap: '20px', 
        alignItems: 'center', 
        marginBottom: '30px',
        padding: '15px',
        backgroundColor: '#40558fff',
        borderRadius: '8px'
      }}>
        <label>
            <Select
                options={['all', 'with_art', 'without_art']}
                value={filter}
                onChange={(e) => handleFilterChange(e.target.value)}
            />
        </label>
        
        <label>
            <Select
                options={['newest', 'oldest', 'name', 'species']}
                value={sort}
                onChange={(e) => handleSortChange(e.target.value)}
            />
        </label>

        <label>
            <Select
                options={['small', 'normal', 'large']}
                value={cardSize}
                onChange={(e) => handleCardSizeChange(e.target.value)}
            />
        </label>

      </div>

      {/* Full-Featured Pagination */}
      {monsters.length > 0 && (
        <div style={{ marginTop: '40px', marginBottom: '40px' }}>
          <FullPagination
            pagination={pagination}
            itemName="monsters"
            itemsPerPageOptions={[6, 12, 24, 48]}
            currentLimit={limit}
            onLimitChange={handleLimitChange}
            layout={PAGINATION_LAYOUTS.FULL}
          />
        </div>
      )}

      {/* Monster Grid */}
      {monsters.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: '10px',
          marginBottom: '30px'
        }}>
          {monsters.map(monster => (
            <MonsterCard
              key={monster.id}
              monster={monster} // ← Clean domain object!
              size={cardSize}
              showPartyToggle={false} // Keep it simple for this test
              onAbilityGenerate={(monsterId) => {
                console.log('🔮 Generate ability for monster:', monsterId);
                // TODO: Implement with useAbilityGeneration hook
              }}
              onExpandCard={(monster) => {
                console.log('🔍 Expand card for monster:', monster.name);
              }}
            />
          ))}
        </div>
      )}


      {/* Full-Featured Pagination */}
      {monsters.length > 0 && (
        <div style={{ marginTop: '40px', marginBottom: '40px' }}>
          <FullPagination
            pagination={pagination}
            itemName="monsters"
            currentLimit={limit}
            onLimitChange={handleLimitChange}
            layout={PAGINATION_LAYOUTS.DEFAULT}
          />
        </div>
      )}

      {/* Debug Info */}
      <div style={{ 
        marginTop: '40px', 
        padding: '15px', 
        backgroundColor: '#315481ff', 
        borderRadius: '8px',
        fontSize: '14px',
        fontFamily: 'monospace'
      }}>
        <h3>🔍 Debug Information</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            {JSON.stringify(monsters[0], null, 2)}
          </div>
        </div>
      </div>

    </div>
  );
}

export default MyCurrentTestScreen;