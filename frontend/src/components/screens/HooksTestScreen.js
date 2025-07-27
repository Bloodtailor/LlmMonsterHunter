// HooksTestScreen - Test the new clean domain hooks architecture
// Tests our final pattern: hooks manage state, useMemo transforms data, components stay simple
// Includes render counting to verify useMemo optimizations work

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { usePagination } from '../../refactored/shared/hooks/usePagination.js';
import {
  useMonsterCollection,
  useMonster,
  useMonsterStats,
  useMonsterAbilities,
  useMonsterCardArt,
  useMonsterTemplates,
  useMonsterGeneration
} from '../../refactored/app/hooks/useMonsters.js';

function HooksTestScreen() {
  // Render counter
  const renderCount = useRef(0);
  renderCount.current += 1;

  // UI state managed by component
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('newest');
  const [selectedMonsterId, setSelectedMonsterId] = useState(null);

  // Domain hooks - provide clean data + state management
  const monsterCollection = useMonsterCollection();
  const individualMonster = useMonster();
  const monsterStats = useMonsterStats();
  const monsterAbilities = useMonsterAbilities();
  const monsterCardArt = useMonsterCardArt();
  const monsterTemplates = useMonsterTemplates();
  const monsterGeneration = useMonsterGeneration();

  // UI pagination hook
  const pagination = usePagination({ 
    limit: 5, // Small limit for testing
    total: monsterCollection.total 
  });

  // Load initial data
  useEffect(() => {
    console.log('🔄 Loading initial data...');
    monsterStats.loadStats('all');
    monsterTemplates.loadTemplates();
  }, []);

  // Load monsters when filter/sort/pagination changes
  useEffect(() => {
    console.log('🔄 Loading monsters with:', { filter, sort, offset: pagination.currentOffset });
    
    monsterCollection.loadMonsters({
      limit: pagination.limit,
      offset: pagination.currentOffset,
      filter: filter !== 'all' ? filter : undefined,
      sort
    });
  }, [filter, sort, pagination.currentOffset]);

  // Load individual monster when selected
  useEffect(() => {
    if (selectedMonsterId) {
      console.log('🔄 Loading monster:', selectedMonsterId);
      individualMonster.loadMonster(selectedMonsterId);
      monsterAbilities.loadAbilities(selectedMonsterId);
      monsterCardArt.loadCardArt(selectedMonsterId);
    }
  }, [selectedMonsterId]);

  // Handle pagination
  const handlePageChange = useCallback((page) => {
    console.log('📄 Going to page:', page);
    pagination.goToPage(page);
    // loadMonsters will be called by useEffect when pagination.currentOffset changes
  }, [pagination.goToPage]);

  // Handle monster selection
  const handleMonsterSelect = useCallback((monsterId) => {
    setSelectedMonsterId(monsterId);
  }, []);

  // Handle generation
  const handleGenerateMonster = useCallback(() => {
    console.log('✨ Generating monster...');
    monsterGeneration.generate({
      prompt_name: 'detailed_monster',
      generate_card_art: true
    });
  }, [monsterGeneration.generate]);

  return (
    <div className="hooks-test-screen" style={{ padding: '20px', fontFamily: 'monospace' }}>
      
      {/* Render Counter */}
      <div style={{ 
        position: 'fixed', 
        top: '10px', 
        right: '10px', 
        background: '#ff6b6b', 
        color: 'white', 
        padding: '10px', 
        borderRadius: '5px',
        fontWeight: 'bold',
        zIndex: 1000
      }}>
        Renders: {renderCount.current}
      </div>

      <h1>🧪 Hooks Architecture Test</h1>
      <p>Testing our final pattern: Domain hooks + Clean data + No awaiting</p>

      {/* Test Controls */}
      <div style={{ background: '#884a4aff', padding: '15px', borderRadius: '5px', marginBottom: '20px' }}>
        <h3>Test Controls</h3>
        
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center', marginBottom: '10px' }}>
          <label>
            Filter: 
            <select value={filter} onChange={(e) => setFilter(e.target.value)} style={{ marginLeft: '5px' }}>
              <option value="all">All</option>
              <option value="with_art">With Art</option>
              <option value="without_art">Without Art</option>
            </select>
          </label>
          
          <label>
            Sort: 
            <select value={sort} onChange={(e) => setSort(e.target.value)} style={{ marginLeft: '5px' }}>
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
              <option value="name">Name</option>
              <option value="species">Species</option>
            </select>
          </label>

          <button onClick={handleGenerateMonster} disabled={monsterGeneration.isGenerating}>
            {monsterGeneration.isGenerating ? '⏳ Generating...' : '✨ Generate Monster'}
          </button>
        </div>

        <div>
          <strong>Current Settings:</strong> Filter={filter}, Sort={sort}, Page={pagination.currentPage}, Limit={pagination.limit}
        </div>
      </div>

      {/* Monster Collection Test */}
      <div style={{ background: '#517e9eff', padding: '15px', borderRadius: '5px', marginBottom: '20px' }}>
        <h3>🐲 Monster Collection Hook Test</h3>
        
        <div style={{ marginBottom: '10px' }}>
          <strong>Status:</strong> {monsterCollection.isLoading ? '🔄 Loading' : monsterCollection.isError ? '❌ Error' : '✅ Loaded'}
          {monsterCollection.error && <span style={{ color: 'red' }}> - {monsterCollection.error.message}</span>}
        </div>

        <div style={{ marginBottom: '10px' }}>
          <strong>Data:</strong> {monsterCollection.monsters.length} monsters of {monsterCollection.total} total
        </div>

        {/* Monster Grid */}
        {monsterCollection.isLoading ? (
          <div>Loading monsters...</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px', margin: '10px 0' }}>
            {monsterCollection.monsters.map(monster => (
              <div 
                key={monster.id} 
                onClick={() => handleMonsterSelect(monster.id)}
                style={{ 
                  padding: '10px', 
                  border: selectedMonsterId === monster.id ? '2px solid #2196f3' : '1px solid #ddd',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  background: selectedMonsterId === monster.id ? '#6696c0ff' : 'white'
                }}
              >
                <strong>{monster.name}</strong><br />
                <small>{monster.species}</small><br />
                <small>🎨 {monster.cardArt.exists ? 'Has Art' : 'No Art'}</small><br />
                <small>⚡ {monster.abilityCount} abilities</small>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', justifyContent: 'center' }}>
          <button 
            onClick={() => handlePageChange(pagination.currentPage - 1)} 
            disabled={!pagination.hasPrev}
          >
            ← Previous
          </button>
          <span>Page {pagination.currentPage} of {pagination.totalPages || '?'}</span>
          <button 
            onClick={() => handlePageChange(pagination.currentPage + 1)} 
            disabled={!pagination.hasNext}
          >
            Next →
          </button>
        </div>

        {/* Raw Data Debug */}
        <details style={{ marginTop: '10px' }}>
          <summary>🔍 Raw Response Debug</summary>
          <pre style={{ background: '#a35d5dff', padding: '10px', fontSize: '12px', overflow: 'auto', maxHeight: '200px' }}>
            {JSON.stringify(monsterCollection.rawResponse, null, 2)}
          </pre>
        </details>
      </div>

      {/* Individual Monster Test */}
      {selectedMonsterId && (
        <div style={{ background: '#bc8ec4ff', padding: '15px', borderRadius: '5px', marginBottom: '20px' }}>
          <h3>🔍 Individual Monster Hook Test</h3>
          
          <div style={{ marginBottom: '10px' }}>
            <strong>Monster ID:</strong> {selectedMonsterId} | 
            <strong> Status:</strong> {individualMonster.isLoading ? '🔄 Loading' : individualMonster.isError ? '❌ Error' : '✅ Loaded'}
          </div>

          {individualMonster.monster && (
            <div style={{ background: 'white', padding: '10px', borderRadius: '5px', marginBottom: '10px' }}>
              <h4>{individualMonster.monster.name}</h4>
              <p><strong>Species:</strong> {individualMonster.monster.species}</p>
              <p><strong>Description:</strong> {individualMonster.monster.description}</p>
              <p><strong>Stats:</strong> ATK {individualMonster.monster.stats.attack}, DEF {individualMonster.monster.stats.defense}, SPD {individualMonster.monster.stats.speed}</p>
              <p><strong>Traits:</strong> {individualMonster.monster.personalityTraits.join(', ')}</p>
            </div>
          )}

          {/* Abilities Test */}
          <div style={{ marginBottom: '10px' }}>
            <strong>Abilities:</strong> {monsterAbilities.isLoading ? '🔄 Loading' : `${monsterAbilities.abilities.length} abilities`}
            {monsterAbilities.abilities.length > 0 && (
              <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                {monsterAbilities.abilities.map(ability => (
                  <li key={ability.id}>
                    <strong>{ability.name}</strong> ({ability.type}) - {ability.description}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Card Art Test */}
          <div>
            <strong>Card Art:</strong> {monsterCardArt.isLoading ? '🔄 Loading' : (
              monsterCardArt.cardArt ? (
                monsterCardArt.cardArt.exists ? 
                  `✅ Exists (${monsterCardArt.cardArt.relativePath})` : 
                  '❌ No art'
              ) : '❓ Unknown'
            )}
          </div>
        </div>
      )}

      {/* Stats Test */}
      <div style={{ background: '#238023ff', padding: '15px', borderRadius: '5px', marginBottom: '20px' }}>
        <h3>📊 Monster Stats Hook Test</h3>
        
        <div style={{ marginBottom: '10px' }}>
          <strong>Status:</strong> {monsterStats.isLoading ? '🔄 Loading' : monsterStats.isError ? '❌ Error' : '✅ Loaded'}
        </div>

        {monsterStats.stats && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
            <div><strong>Total Monsters:</strong> {monsterStats.stats.overview.totalMonsters}</div>
            <div><strong>Total Abilities:</strong> {monsterStats.stats.overview.totalAbilities}</div>
            <div><strong>Unique Species:</strong> {monsterStats.stats.overview.uniqueSpecies}</div>
            <div><strong>With Card Art:</strong> {monsterStats.stats.overview.withCardArt}</div>
            <div><strong>Without Card Art:</strong> {monsterStats.stats.overview.withoutCardArt}</div>
            <div><strong>Avg Abilities:</strong> {monsterStats.stats.overview.avgAbilitiesPerMonster.toFixed(1)}</div>
          </div>
        )}
      </div>

      {/* Templates Test */}
      <div style={{ background: '#77551eff', padding: '15px', borderRadius: '5px', marginBottom: '20px' }}>
        <h3>📝 Monster Templates Hook Test</h3>
        
        <div style={{ marginBottom: '10px' }}>
          <strong>Status:</strong> {monsterTemplates.isLoading ? '🔄 Loading' : monsterTemplates.isError ? '❌ Error' : '✅ Loaded'}
        </div>

        {monsterTemplates.templates && Object.keys(monsterTemplates.templates).length > 0 && (
          <div>
            <strong>Available Templates:</strong> {Object.keys(monsterTemplates.templates).join(', ')}
          </div>
        )}
      </div>

      {/* Generation Test */}
      <div style={{ background: '#d14272ff', padding: '15px', borderRadius: '5px', marginBottom: '20px' }}>
        <h3>✨ Monster Generation Hook Test</h3>
        
        <div style={{ marginBottom: '10px' }}>
          <strong>Status:</strong> {monsterGeneration.isGenerating ? '🔄 Generating' : monsterGeneration.isError ? '❌ Error' : '✅ Ready'}
        </div>

        {monsterGeneration.generationResult && (
          <div style={{ background: 'white', padding: '10px', borderRadius: '5px' }}>
            <strong>Generation Result:</strong> {monsterGeneration.generationResult.success ? '✅ Success' : '❌ Failed'}
            {monsterGeneration.monster && (
              <div style={{ marginTop: '10px' }}>
                <strong>Generated Monster:</strong> {monsterGeneration.monster.name} ({monsterGeneration.monster.species})
              </div>
            )}
          </div>
        )}
      </div>

      {/* Architecture Summary */}
      <div style={{ background: '#6e8f9eff', padding: '15px', borderRadius: '5px' }}>
        <h3>🏗️ Architecture Test Summary</h3>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          <li>✅ Hooks manage state (raw + clean data)</li>
          <li>✅ Components don't await anything</li>
          <li>✅ useMemo prevents unnecessary re-transforms</li>
          <li>✅ Both raw and clean data available</li>
          <li>✅ Pagination coordinated by component</li>
          <li>✅ Transformers stay pure functions</li>
          <li>✅ Error and loading states handled automatically</li>
        </ul>
        
        <div style={{ marginTop: '10px', fontWeight: 'bold' }}>
          Watch the render counter in top-right - it should stay low even when changing filters/pages!
        </div>
      </div>

    </div>
  );
}

export default HooksTestScreen;