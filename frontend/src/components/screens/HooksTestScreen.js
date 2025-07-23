// Hooks Test Screen - Test the new monster hooks with clean transformed data
// Shows side-by-side comparison of loading states, errors, and clean game objects
// Perfect for verifying the hook architecture works correctly

import React, { useState } from 'react';
import {
  useMonsterCollection,
  useMonster,
  useMonsterStats,
  useMonsterAbilities,
  useMonsterCardArt,
  useMonsterTemplates,
  useMonsterGeneration,
  useAbilityGeneration,
  useMonsters
} from '../../refactored/app/hooks/useMonsters.js';

function HooksTestScreen() {
  // Test configuration state
  const [selectedMonsterId, setSelectedMonsterId] = useState(174); // Default to test monster
  const [collectionFilter, setCollectionFilter] = useState('all');
  const [collectionSort, setCollectionSort] = useState('newest');
  const [collectionLimit, setCollectionLimit] = useState(5);
  const [statsFilter, setStatsFilter] = useState('all');

  // Test individual hooks
  const collection = useMonsterCollection({
    limit: collectionLimit,
    filter: collectionFilter,
    sort: collectionSort
  });

  const individual = useMonster(selectedMonsterId);
  const stats = useMonsterStats(statsFilter);
  const abilities = useMonsterAbilities(selectedMonsterId);
  const cardArt = useMonsterCardArt(selectedMonsterId);
  const templates = useMonsterTemplates();
  const generation = useMonsterGeneration();
  const abilityGeneration = useAbilityGeneration();

  // Test combined hook
  const combined = useMonsters({
    collection: { limit: 3, filter: 'with_art' },
    statsFilter: 'all',
    loadStats: true,
    loadTemplates: true
  });

  // Helper function to format display data
  const formatData = (data) => {
    if (!data) return 'null';
    return JSON.stringify(data, null, 2);
  };

  // Test generation functions
  const handleGenerateMonster = async () => {
    try {
      await generation.generate({
        prompt_name: 'detailed_monster',
        generate_card_art: true
      });
    } catch (error) {
      console.error('Generation failed:', error);
    }
  };

  const handleGenerateAbility = async () => {
    if (!selectedMonsterId) {
      alert('Select a monster ID first');
      return;
    }
    
    try {
      await abilityGeneration.generate(selectedMonsterId);
    } catch (error) {
      console.error('Ability generation failed:', error);
    }
  };

  return (
    <div className="hooks-test-screen">
      <div className="test-header">
        <h1>🪝 Monster Hooks Test Suite</h1>
        <p>Testing transformed monster data from the new hook architecture</p>
      </div>

      {/* Test Configuration */}
      <div className="test-config">
        <h2>🔧 Test Configuration</h2>
        <div className="config-grid">
          <div className="config-item">
            <label>Monster ID for Individual Tests:</label>
            <input 
              type="number" 
              value={selectedMonsterId} 
              onChange={(e) => setSelectedMonsterId(parseInt(e.target.value) || null)}
            />
          </div>
          
          <div className="config-item">
            <label>Collection Filter:</label>
            <select value={collectionFilter} onChange={(e) => setCollectionFilter(e.target.value)}>
              <option value="all">All</option>
              <option value="with_art">With Card Art</option>
              <option value="without_art">Without Card Art</option>
            </select>
          </div>
          
          <div className="config-item">
            <label>Collection Sort:</label>
            <select value={collectionSort} onChange={(e) => setCollectionSort(e.target.value)}>
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
              <option value="name">Name</option>
              <option value="species">Species</option>
            </select>
          </div>
          
          <div className="config-item">
            <label>Collection Limit:</label>
            <input 
              type="number" 
              min="1" 
              max="20" 
              value={collectionLimit} 
              onChange={(e) => setCollectionLimit(parseInt(e.target.value) || 5)}
            />
          </div>
        </div>
      </div>

      {/* Hook Tests Grid */}
      <div className="hooks-test-grid">
        
        {/* Monster Collection Hook */}
        <div className="hook-test-card">
          <h3>📋 useMonsterCollection</h3>
          <div className="hook-status">
            <span className={`status ${collection.isLoading ? 'loading' : collection.isError ? 'error' : 'success'}`}>
              {collection.isLoading ? '🔄 Loading' : collection.isError ? '❌ Error' : '✅ Success'}
            </span>
            <span>Monsters: {collection.monsters?.length || 0}</span>
            <span>Total: {collection.pagination?.total || 0}</span>
          </div>
          
          {collection.pagination && (
            <div className="pagination-test">
              <button 
                onClick={collection.prevPage} 
                disabled={!collection.pagination.hasPrevPage}
              >
                ⬅️ Prev
              </button>
              <span>Page {collection.pagination.currentPage}/{collection.pagination.totalPages}</span>
              <button 
                onClick={collection.nextPage} 
                disabled={!collection.pagination.hasNextPage}
              >
                Next ➡️
              </button>
            </div>
          )}
          
          <details>
            <summary>📊 Data Structure</summary>
            <pre className="data-display">{formatData({
              monsters: collection.monsters?.slice(0, 2), // Show first 2
              pagination: collection.pagination,
              filters: collection.filters
            })}</pre>
          </details>
          
          {collection.isError && (
            <div className="error-display">
              Error: {collection.error?.message}
            </div>
          )}
        </div>

        {/* Individual Monster Hook */}
        <div className="hook-test-card">
          <h3>🐲 useMonster</h3>
          <div className="hook-status">
            <span className={`status ${individual.isLoading ? 'loading' : individual.isError ? 'error' : 'success'}`}>
              {individual.isLoading ? '🔄 Loading' : individual.isError ? '❌ Error' : '✅ Success'}
            </span>
            {individual.monster && (
              <span>Monster: {individual.monster.name}</span>
            )}
          </div>
          
          <details>
            <summary>📊 Clean Monster Object</summary>
            <pre className="data-display">{formatData(individual.monster)}</pre>
          </details>
          
          {individual.isError && (
            <div className="error-display">
              Error: {individual.error?.message}
            </div>
          )}
        </div>

        {/* Monster Stats Hook */}
        <div className="hook-test-card">
          <h3>📈 useMonsterStats</h3>
          <div className="hook-status">
            <span className={`status ${stats.isLoading ? 'loading' : stats.isError ? 'error' : 'success'}`}>
              {stats.isLoading ? '🔄 Loading' : stats.isError ? '❌ Error' : '✅ Success'}
            </span>
            {stats.stats && (
              <span>Total: {stats.stats.overview?.totalMonsters}</span>
            )}
          </div>
          
          <details>
            <summary>📊 Stats Overview</summary>
            <pre className="data-display">{formatData(stats.stats?.overview)}</pre>
          </details>
          
          {stats.isError && (
            <div className="error-display">
              Error: {stats.error?.message}
            </div>
          )}
        </div>

        {/* Monster Abilities Hook */}
        <div className="hook-test-card">
          <h3>⚡ useMonsterAbilities</h3>
          <div className="hook-status">
            <span className={`status ${abilities.isLoading ? 'loading' : abilities.isError ? 'error' : 'success'}`}>
              {abilities.isLoading ? '🔄 Loading' : abilities.isError ? '❌ Error' : '✅ Success'}
            </span>
            <span>Count: {abilities.count}</span>
          </div>
          
          <details>
            <summary>📊 Abilities Array</summary>
            <pre className="data-display">{formatData(abilities.abilities)}</pre>
          </details>
          
          {abilities.isError && (
            <div className="error-display">
              Error: {abilities.error?.message}
            </div>
          )}
        </div>

        {/* Card Art Hook */}
        <div className="hook-test-card">
          <h3>🎨 useMonsterCardArt</h3>
          <div className="hook-status">
            <span className={`status ${cardArt.isLoading ? 'loading' : cardArt.isError ? 'error' : 'success'}`}>
              {cardArt.isLoading ? '🔄 Loading' : cardArt.isError ? '❌ Error' : '✅ Success'}
            </span>
            {cardArt.cardArt && (
              <span>Exists: {cardArt.cardArt.exists ? '✅' : '❌'}</span>
            )}
          </div>
          
          <details>
            <summary>📊 Card Art Object</summary>
            <pre className="data-display">{formatData(cardArt.cardArt)}</pre>
          </details>
          
          {cardArt.isError && (
            <div className="error-display">
              Error: {cardArt.error?.message}
            </div>
          )}
        </div>

        {/* Templates Hook */}
        <div className="hook-test-card">
          <h3>📝 useMonsterTemplates</h3>
          <div className="hook-status">
            <span className={`status ${templates.isLoading ? 'loading' : templates.isError ? 'error' : 'success'}`}>
              {templates.isLoading ? '🔄 Loading' : templates.isError ? '❌ Error' : '✅ Success'}
            </span>
            <span>Templates: {Object.keys(templates.templates).length}</span>
          </div>
          
          <details>
            <summary>📊 Available Templates</summary>
            <pre className="data-display">{formatData(templates.templates)}</pre>
          </details>
          
          {templates.isError && (
            <div className="error-display">
              Error: {templates.error?.message}
            </div>
          )}
        </div>

      </div>

      {/* Generation Tests */}
      <div className="generation-tests">
        <h2>🎲 Generation Mutations</h2>
        
        <div className="generation-grid">
          {/* Monster Generation */}
          <div className="generation-card">
            <h4>🐲 Generate Monster</h4>
            <button 
              onClick={handleGenerateMonster}
              disabled={generation.isGenerating}
              className="btn btn-primary"
            >
              {generation.isGenerating ? '🔄 Generating...' : '✨ Generate Monster'}
            </button>
            
            {generation.generationResult && (
              <div className="generation-result">
                <strong>Result:</strong> {generation.generationResult.success ? '✅ Success' : '❌ Failed'}
                {generation.generationResult.monster && (
                  <div>Generated: {generation.generationResult.monster.name}</div>
                )}
              </div>
            )}
            
            {generation.isError && (
              <div className="error-display">
                Error: {generation.error?.message}
              </div>
            )}
          </div>

          {/* Ability Generation */}
          <div className="generation-card">
            <h4>⚡ Generate Ability</h4>
            <button 
              onClick={handleGenerateAbility}
              disabled={abilityGeneration.isGenerating || !selectedMonsterId}
              className="btn btn-primary"
            >
              {abilityGeneration.isGenerating ? '🔄 Generating...' : '✨ Generate Ability'}
            </button>
            
            {abilityGeneration.generationResult && (
              <div className="generation-result">
                <strong>Result:</strong> {abilityGeneration.generationResult.success ? '✅ Success' : '❌ Failed'}
                {abilityGeneration.generationResult.ability && (
                  <div>Generated: {abilityGeneration.generationResult.ability.name}</div>
                )}
              </div>
            )}
            
            {abilityGeneration.isError && (
              <div className="error-display">
                Error: {abilityGeneration.error?.message}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Combined Hook Test */}
      <div className="combined-test">
        <h2>🔗 useMonsters (Combined Hook)</h2>
        <div className="combined-status">
          <span>Collection: {combined.collection.isLoading ? '🔄' : '✅'} ({combined.collection.monsters?.length || 0})</span>
          <span>Stats: {combined.stats.isLoading ? '🔄' : '✅'} ({combined.stats.stats?.overview?.totalMonsters || 0})</span>
          <span>Templates: {combined.templates.isLoading ? '🔄' : '✅'} ({Object.keys(combined.templates.templates || {}).length})</span>
        </div>
        
        <details>
          <summary>📊 Combined Data Structure</summary>
          <pre className="data-display">{formatData({
            collection: {
              monsters: combined.collection.monsters?.slice(0, 1),
              pagination: combined.collection.pagination
            },
            stats: combined.stats.stats?.overview,
            templates: combined.templates.templates
          })}</pre>
        </details>
      </div>

      {/* Instructions */}
      <div className="test-instructions">
        <h2>📋 Testing Instructions</h2>
        <ol>
          <li>🔍 <strong>Verify Clean Data:</strong> Check that all objects use camelCase</li>
          <li>📄 <strong>Test Pagination:</strong> Use prev/next buttons to test collection pagination</li>
          <li>🎯 <strong>Individual Loading:</strong> Change Monster ID to test individual monster loading</li>
          <li>🎲 <strong>Test Generation:</strong> Generate monsters and abilities to test mutations</li>
          <li>🔄 <strong>Loading States:</strong> Watch loading indicators during API calls</li>
          <li>❌ <strong>Error Handling:</strong> Try invalid monster ID (e.g., 999999) to test errors</li>
          <li>⚙️ <strong>Filters/Sorting:</strong> Change collection options to test different data</li>
        </ol>
      </div>

    </div>
  );
}

export default HooksTestScreen;