// MyCurrentTestScreen - FOCUSED ARCHITECTURE TEST WITH MONSTER GENERATION
// Tests our complete refactored architecture: useMonsterCollection + useMonsterGeneration + Full Pagination + MonsterCard + MonsterCardViewer
// Added big generate monster button using useMonsterGeneration hook

import React, { useState, useEffect, useCallback } from "react";
import { usePagination } from "../../shared/ui/Pagination/usePagination.js";
import FullPagination, { PAGINATION_LAYOUTS } from "../../shared/ui/Pagination/PaginationPresets.js";
import { useMonsterCardViewer } from "../../components/cards/useMonsterCardViewer.js";
import { useParty } from '../../app/contexts/PartyContext/index.js';
import { 
  Select,
  EmptyState,
  EMPTY_STATE_PRESETS,
  Card,
  LoadingSpinner
} from "../../shared/ui/index.js";

function MonsterPoolDisplay( {style = {} }) {
  // UI state
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('newest');
  const [limit, setLimit] = useState(12);
  const [cardSize, setCardSize] = useState('md');
  const [itemsPerPageOptions, setItemsPerPageOptions ] = useState([6, 12, 24, 48]);

  //hooks
  const { MonsterCard, viewer } = useMonsterCardViewer();
  const { party, followingMonsters, followingSize, loadingFollowers } = useParty();
  const pagination = usePagination({ 
    limit, 
    total: followingSize 
  });

  // Handlers
  const handleLimitChange = useCallback((newLimit) => {
    setLimit(newLimit);
    pagination.firstPage();
  }, [pagination.firstPage]);

  const handleFilterChange = useCallback((newFilter) => {
    setFilter(newFilter);
    pagination.firstPage(); 
  }, [pagination.firstPage]);

  const handleSortChange = useCallback((newSort) => {
    setSort(newSort);
    pagination.firstPage(); 
  }, [pagination.firstPage]);

  const handleCardSizeChange = useCallback((newCardSize) => {
    setCardSize(newCardSize);
    
    if (newCardSize === 'sm' ){
        setItemsPerPageOptions([10, 20, 50, 100])
        setLimit(10)

    } else {
        setItemsPerPageOptions([6, 12, 24, 48])
        setLimit(12)
    }
  }, []);

  // Filter the following monsters list with our settings
  const filteredMonsters = followingMonsters.filter( (monster) => !party.includes(monster.id) ) 
  const paginatedMonsters = filteredMonsters.slice(
    pagination.currentOffset,
    pagination.currentOffset + pagination.limit
  );

  return (
    <div style={style}>
      {/* Controls */}
      <Card >
        <div style={{
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
        </div>

      </Card>

      {/* Full-Featured Pagination (Top) */}
      {followingSize > 0 && (
          <FullPagination
            pagination={pagination}
            itemName="monsters"
            itemsPerPageOptions={itemsPerPageOptions}
            currentLimit={limit}
            onLimitChange={handleLimitChange}
            layout={PAGINATION_LAYOUTS.FULL}
          />
      )}

      {/* Monster Grid */}
      { loadingFollowers ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <LoadingSpinner size="section" type="cardFlip"/>
        </div>
      ) : followingSize === 0 ? (
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
          {paginatedMonsters.map(monster => (
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
      {followingSize > 0 && (
        <FullPagination
          pagination={pagination}
          itemName="monsters"
          currentLimit={limit}
          onLimitChange={handleLimitChange}
          layout={PAGINATION_LAYOUTS.DEFAULT}
        />
      )}

      {viewer}
    </div>
  );
}

export default MonsterPoolDisplay;