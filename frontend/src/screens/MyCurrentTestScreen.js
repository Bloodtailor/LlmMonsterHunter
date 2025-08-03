// MyCurrentTestScreen - FOCUSED ARCHITECTURE TEST WITH MONSTER GENERATION
// Tests our complete refactored architecture: useMonsterCollection + useMonsterGeneration + Full Pagination + MonsterCard + MonsterCardViewer
// Added big generate monster button using useMonsterGeneration hook

import React, { useState, useEffect, useCallback } from "react";
import { usePagination } from "../shared/ui/Pagination/usePagination.js";
import { useMonsterCollection, useMonsterGeneration } from "../app/hooks/useMonsters.js";
import FullPagination, { PAGINATION_LAYOUTS } from "../shared/ui/Pagination/PaginationPresets.js";
import { 
  Select,
  Alert,
  EmptyState,
  Button,
  StatusBadge,
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

  // Monster generation hook
  const {
    generationResult,
    monster: generatedMonster,
    isGenerating,
    isError: isGenerationError,
    error: generationError,
    generate
  } = useMonsterGeneration();

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

  // Refresh monster list after successful generation
  useEffect(() => {
    if (generationResult?.success && generatedMonster) {
      console.log('✅ Monster generated successfully, refreshing list...');
      // Go to first page to see the new monster (newest first)
      pagination.firstPage();
      // Reload will happen automatically due to pagination change
    }
  }, [generationResult?.success, generatedMonster, pagination.firstPage]);

  // Handle monster generation
  const handleGenerateMonster = useCallback(async () => {
    console.log('🎲 Generating new monster...');
    await generate({
      prompt_name: 'detailed_monster',
      generate_card_art: true
    });
  }, [generate]);

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
        <p>Testing: useMonsterCollection + useMonsterGeneration + Full-Featured Pagination + Refactored MonsterCard + MonsterCardViewer</p>
      </div>

      {/* Big Generate Monster Button */}
      <div style={{ 
        marginBottom: '40px', 
        textAlign: 'center',
        padding: '30px',
        backgroundColor: '#2a3441ff',
        borderRadius: '12px',
        border: '2px solid #40558fff'
      }}>
        <h2 style={{ marginBottom: '20px', color: '#e2e8f0' }}>🎲 Generate New Monster</h2>
        
        <Button
          variant="primary"
          size="lg"
          onClick={handleGenerateMonster}
          disabled={isGenerating}
          style={{
            fontSize: '18px',
            padding: '16px 32px',
            minWidth: '250px'
          }}
        >
          {isGenerating ? (
            <>
              <span style={{ marginRight: '10px' }}>🔄</span>
              Generating Monster...
            </>
          ) : (
            <>
              <span style={{ marginRight: '10px' }}>✨</span>
              Generate New Monster
            </>
          )}
        </Button>

        {/* Generation Status */}
        <div style={{ marginTop: '20px' }}>
          {isGenerating && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
              <StatusBadge status="warning" size="md" />
              <span style={{ color: '#e2e8f0' }}>Creating your monster with AI...</span>
            </div>
          )}

          {generationResult?.success && generatedMonster && (
            <Alert type="success" size="md" style={{ maxWidth: '500px', margin: '0 auto' }}>
              <strong>🎉 Success!</strong> Generated "{generatedMonster.name}" - {generatedMonster.species}
            </Alert>
          )}

          {isGenerationError && (
            <Alert type="error" size="md" style={{ maxWidth: '500px', margin: '0 auto' }}>
              <strong>❌ Generation Failed:</strong> {generationError?.message || 'Unknown error occurred'}
            </Alert>
          )}
        </div>
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
              showPartyToggle={true} // Keep it simple for this test
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
              <li>✅ useMonsterGeneration hook</li>
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
              <li>Generating: {isGenerating ? 'Yes' : 'No'}</li>
              {generatedMonster && <li>Last Generated: {generatedMonster.name}</li>}
            </ul>
          </div>
        </div>
      </div>

    </div>
  );
}

export default MyCurrentTestScreen;