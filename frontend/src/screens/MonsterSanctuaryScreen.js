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
  Scroll,
  EMPTY_STATE_PRESETS,
  Card,
  CardSection,
  LoadingSpinner
} from "../shared/ui/index.js";

// Import our new components
import { useMonsterCardViewer } from "../components/cards/useMonsterCardViewer.js";

function MonsterSanctuaryScreen() {
  // UI state
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('newest');
  const [limit, setLimit] = useState(12);
  const [cardSize, setCardSize] = useState('md');

  const { MonsterCard, viewer } = useMonsterCardViewer();

  // Domain hook - provides clean monster data
  const {
    monsters,
    total,
    isLoading,
    isError,
    error,
    loadMonsters
  } = useMonsterCollection();

  // Monster generation hook
  const {
    monster: generatedMonster,
    isGenerating,
    generate
  } = useMonsterGeneration();

  // Pagination hook
  const pagination = usePagination({ 
    limit, 
    total 
  });

  // Load monsters when filters or pagination changes
  const loadMonstersWithPagination = useCallback(() => {
    loadMonsters({
      limit,
      offset: pagination.currentOffset,
      filter: filter !== 'all' ? filter : undefined,
      sort
    });
  }, [filter, sort, limit, pagination.currentOffset, loadMonsters, generatedMonster]);

  // Auto-load on mount and when dependencies change
  useEffect(() => {
    loadMonstersWithPagination();
  }, [loadMonstersWithPagination]);

  // Handle monster generation
  const handleGenerateMonster = useCallback(async () => {
    console.log('🎲 Generating new monster...');
    await generate({
      prompt_name: 'detailed_monster',
      generate_card_art: true
    });
    pagination.firstPage();
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
    <div>
      
      {/* Header */}
      <Card size="xl" variant="elevated" background="light">
        <CardSection 
          title='🏛️ Monster Sanctuary'
          type='header'
          size='xl'
          alignment='center'
        >

          <p>Welcome to your mystical sanctuary where legendary creatures await your discovery. Each monster is unique with its own personality, abilities, and backstory.</p>
          <div style={{marginTop: '24px'}}>
            <Button 
              variant="primary"
              size="xl"
              onClick={handleGenerateMonster}
              disabled={isGenerating}
              >
              {isGenerating ? (
                <>
                  <span style={{ marginRight: '10px' }}><LoadingSpinner size='xl' type="spin" color="secondary"/></span>
                  Summoning New Monster...
                </>
              ) : (
                <>
                  <span style={{ marginRight: '10px' }}>✨</span>
                  Summon New Monster
                </>
              )}
            </Button>
          </div>
        </CardSection>
      </Card>

      {/* Controls */}
      <Card style={{
          marginTop: '16px',
          display: 'flex',
          flexDirection: 'row',
          gap: '10px'
        }}>
        <label style={{width: '150px'}}>
          Filter:
          <Select
            options={['all', 'with_art', 'without_art']}
            value={filter}
            onChange={(e) => handleFilterChange(e.target.value)}
          />
        </label>
        
        <label style={{width: '150px'}}>
          Sort:
          <Select
            options={['newest', 'oldest', 'name', 'species']}
            value={sort}
            onChange={(e) => handleSortChange(e.target.value)}
          />
        </label>

        <label style={{width: '150px'}}>
          Size:
          <Select
            options={['sm', 'md', 'lg', 'xl']}
            value={cardSize}
            onChange={(e) => handleCardSizeChange(e.target.value)}
          />
        </label>

      </Card>

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
      { isError ? (
        <Alert type="error" title="Loading Error" style={{ marginBottom: '20px' }}>
          {error?.message || 'Failed to load monsters'}
        </Alert>
      ) : isLoading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <LoadingSpinner size="section" type="cardFlip"/>
        </div>
      ) : monsters.length === 0 ? (
        <EmptyState
          {...EMPTY_STATE_PRESETS.NO_MONSTERS}
          size="lg"
          style={{ margin: '40px 0' }}
        />
      ) : (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-evenly', 
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
    </div>
  );
}

export default MonsterSanctuaryScreen;