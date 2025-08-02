// MyCurrentTestScreen - FOCUSED ARCHITECTURE TEST WITH CARD VIEWER
// Tests our complete refactored architecture: useMonsterCollection + Full Pagination + MonsterCard + MonsterCardViewer
// Simple and focused - just pagination with monster cards + beautiful modal viewer

import React, { useState, useEffect, useCallback } from "react";
import { usePagination } from "../shared/ui/Pagination/usePagination.js";
import { useMonsterCollection } from "../app/hooks/useMonsters.js";
import FullPagination, { PAGINATION_LAYOUTS } from "../shared/ui/Pagination/PaginationPresets.js";
import { 
  Select,
  Alert,
  EmptyState,
  EMPTY_STATE_PRESETS
} from "../shared/ui/index.js";

// Import our new components
import { useMonsterCardViewer } from "../components/cards/useMonsterCardViewer.js";

function MyCurrentTestScreen() {
  // UI state
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('newest');
  const [limit, setLimit] = useState(12);
  const [cardSize, setCardSize] = useState('md');

  const { MonsterCard, viewer } = useMonsterCardViewer();

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
        <p>Testing: useMonsterCollection + Full-Featured Pagination + Refactored MonsterCard + MonsterCardViewer</p>
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
          Filter:
          <Select
            options={['all', 'with_art', 'without_art']}
            value={filter}
            onChange={(e) => handleFilterChange(e.target.value)}
          />
        </label>
        
        <label>
          Sort:
          <Select
            options={['newest', 'oldest', 'name', 'species']}
            value={sort}
            onChange={(e) => handleSortChange(e.target.value)}
          />
        </label>

        <label>
          Size:
          <Select
            options={['sm', 'md', 'lg', 'xl']}
            value={cardSize}
            onChange={(e) => handleCardSizeChange(e.target.value)}
          />
        </label>

      </div>

      {/* Error State */}
      {isError && (
        <Alert type="error" title="Loading Error" style={{ marginBottom: '20px' }}>
          {error?.message || 'Failed to load monsters'}
        </Alert>
      )}

      {/* Loading State */}
      {isLoading && (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div>🔄 Loading monsters...</div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !isError && monsters.length === 0 && (
        <EmptyState
          {...EMPTY_STATE_PRESETS.NO_MONSTERS}
          size="lg"
          style={{ margin: '40px 0' }}
        />
      )}

      {/* Full-Featured Pagination (Top) */}
      {monsters.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
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
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
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
            />
          ))}
        </div>
      )}

      {/* Full-Featured Pagination (Bottom) */}
      {monsters.length > 0 && (
        <div style={{ marginTop: '40px', marginBottom: '40px' }}>
          <FullPagination
            pagination={pagination}
            itemName="monsters"
            currentLimit={limit}
            onLimitChange={handleLimitChange}
            layout={PAGINATION_LAYOUTS.DEFAULT}
          />
          {viewer}
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
            <strong>Clean Architecture Status:</strong>
            <ul>
              <li>✅ useMonsterCollection hook</li>
              <li>✅ Clean domain objects</li>
              <li>✅ Full-featured pagination</li>
              <li>✅ MonsterCard with callback pattern</li>
              <li>✅ MonsterCardViewer (no circular deps!)</li>
              <li>✅ UI primitives</li>
            </ul>
          </div>
          <div>
            <strong>Current State:</strong>
            <ul>
              <li>Monsters: {monsters.length}/{total}</li>
              <li>Page: {pagination.currentPage}/{pagination.totalPages}</li>
              <li>Filter: {filter}</li>
              <li>Sort: {sort}</li>
              <li>Card Size: {cardSize}</li>
            </ul>
          </div>
        </div>
      </div>

    </div>
  );
}

export default MyCurrentTestScreen;