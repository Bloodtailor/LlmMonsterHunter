// FilterControls Examples Component - Showcase FilterSelectGroup component variations
// Interactive examples and builder for dynamic filter dropdown generation
// Perfect for development reference and testing different filter configurations

import React, { useState } from 'react';
import { FilterSelectGroup } from '../../shared/ui/FilterControls/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField, Input } from '../../shared/ui/Form/index.js';
import { Badge } from '../../shared/ui/Badge/index.js';
import { Alert } from '../../shared/ui/Feedback/index.js';

function FilterControlsExamples() {
  // Example filter options for different use cases
  const monsterFilterOptions = {
    species: ['Dragon', 'Beast', 'Elemental', 'Undead', 'Fey'],
    element: {
      fire: 'Fire 🔥',
      water: 'Water 💧',
      earth: 'Earth 🌍',
      air: 'Air 💨',
      dark: 'Dark 🌑',
      light: 'Light ✨'
    },
    rarity: ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary'],
    level_range: ['1-10', '11-20', '21-30', '31-40', '41-50']
  };

  const generationFilterOptions = {
    generation_type: ['LLM', 'Template', 'Random'],
    priority: [1, 2, 3, 4, 5],
    status: ['Pending', 'Processing', 'Completed', 'Failed'],
    prompt_name: ['Basic Monster', 'Elite Creature', 'Boss Fight', 'Companion']
  };

  // State for examples
  const [monsterFilters, setMonsterFilters] = useState({});
  const [generationFilters, setGenerationFilters] = useState({ priority: 3 });
  const [customFilters, setCustomFilters] = useState({});

  // Interactive builder state
  const [builderConfig, setBuilderConfig] = useState({
    layout: 'grid',
    disabled: false,
    showPlaceholders: true,
    optionFormat: 'array' // 'array' or 'object'
  });

  const [builderFilters, setBuilderFilters] = useState({
    category: 'Equipment',
    quality: 'Rare'
  });

  // Dynamic filter options for builder
  const builderFilterOptions = {
    category: builderConfig.optionFormat === 'array' 
      ? ['Weapon', 'Armor', 'Accessory', 'Consumable', 'Equipment']
      : {
          weapon: 'Weapon ⚔️',
          armor: 'Armor 🛡️',
          accessory: 'Accessory 💍',
          consumable: 'Consumable 🧪',
          equipment: 'Equipment 🎒'
        },
    quality: ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary'],
    level: [1, 5, 10, 15, 20, 25, 30]
  };

  // Handle filter changes
  const handleMonsterFilterChange = (fieldName, value, allValues) => {
    setMonsterFilters(allValues);
  };

  const handleGenerationFilterChange = (fieldName, value, allValues) => {
    setGenerationFilters(allValues);
  };

  const handleCustomFilterChange = (fieldName, value, allValues) => {
    setCustomFilters(allValues);
  };

  const handleBuilderFilterChange = (fieldName, value, allValues) => {
    setBuilderFilters(allValues);
  };

  const handleBuilderConfigChange = (field, value) => {
    setBuilderConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Card size="lg" padding="lg" className="filter-controls-examples">
      <CardSection type="header" title="FilterControls Components Showcase" />
      
      {/* Basic Layout Examples */}
      <CardSection type="content" title="Layout Variations">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          {/* Grid Layout */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>
              Grid Layout (Default)
              <Badge size="sm" variant="info" style={{ marginLeft: '8px' }}>
                Auto-sizing columns
              </Badge>
            </h4>
            <FilterSelectGroup
              filterOptions={monsterFilterOptions}
              values={monsterFilters}
              onChange={handleMonsterFilterChange}
              layout="grid"
            />
            <div style={{ 
              marginTop: '12px', 
              fontSize: '14px', 
              color: 'var(--color-text-secondary)',
              fontFamily: 'var(--font-family-mono)'
            }}>
              Active Filters: {JSON.stringify(monsterFilters, null, 2)}
            </div>
          </div>

          {/* Horizontal Layout */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>
              Horizontal Layout
              <Badge size="sm" variant="warning" style={{ marginLeft: '8px' }}>
                Inline, wraps on small screens
              </Badge>
            </h4>
            <FilterSelectGroup
              filterOptions={generationFilterOptions}
              values={generationFilters}
              onChange={handleGenerationFilterChange}
              layout="horizontal"
              customLabels={{
                generation_type: 'Type',
                prompt_name: 'Template'
              }}
            />
            <div style={{ 
              marginTop: '12px', 
              fontSize: '14px', 
              color: 'var(--color-text-secondary)',
              fontFamily: 'var(--font-family-mono)'
            }}>
              Active Filters: {JSON.stringify(generationFilters, null, 2)}
            </div>
          </div>

          {/* Vertical Layout */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>
              Vertical Layout
              <Badge size="sm" variant="success" style={{ marginLeft: '8px' }}>
                Stacked, full width
              </Badge>
            </h4>
            <div style={{ maxWidth: '300px' }}>
              <FilterSelectGroup
                filterOptions={{
                  difficulty: ['Easy', 'Medium', 'Hard', 'Expert'],
                  game_mode: ['Story', 'Arena', 'Survival', 'Custom'],
                  players: ['1 Player', '2 Players', '3 Players', '4 Players']
                }}
                values={customFilters}
                onChange={handleCustomFilterChange}
                layout="vertical"
              />
            </div>
            <div style={{ 
              marginTop: '12px', 
              fontSize: '14px', 
              color: 'var(--color-text-secondary)',
              fontFamily: 'var(--font-family-mono)'
            }}>
              Active Filters: {JSON.stringify(customFilters, null, 2)}
            </div>
          </div>
        </div>
      </CardSection>

      {/* Option Format Examples */}
      <CardSection type="content" title="Option Format Types">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <Alert type="info" title="Two Ways to Define Options">
            <div>
              <p><strong>Array Format:</strong> Simple list of values</p>
              <code style={{ display: 'block', margin: '8px 0', fontFamily: 'var(--font-family-mono)', fontSize: '12px' }}>
                species: ['Dragon', 'Beast', 'Elemental']
              </code>
              
              <p><strong>Object Format:</strong> Value-label pairs with icons/custom text</p>
              <code style={{ display: 'block', margin: '8px 0', fontFamily: 'var(--font-family-mono)', fontSize: '12px' }}>
                element: {`{ fire: 'Fire 🔥', water: 'Water 💧' }`}
              </code>
            </div>
          </Alert>

          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>
              Mixed Format Example
            </h4>
            <FilterSelectGroup
              filterOptions={{
                // Array format
                category: ['Adventure', 'Combat', 'Exploration', 'Social'],
                // Object format with emojis
                theme: {
                  fantasy: 'Fantasy ⚔️',
                  scifi: 'Sci-Fi 🚀',
                  horror: 'Horror 👻',
                  mystery: 'Mystery 🔍'
                },
                // Array format with numbers
                duration: [15, 30, 45, 60, 90, 120]
              }}
              values={{}}
              onChange={() => {}}
              customLabels={{
                duration: 'Duration (minutes)'
              }}
            />
          </div>
        </div>
      </CardSection>

      {/* Interactive Builder */}
      <CardSection type="content" title="Interactive FilterSelectGroup Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '24px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            border: '2px dashed var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Your Filter Group</h4>
            <FilterSelectGroup
              filterOptions={builderFilterOptions}
              values={builderFilters}
              onChange={handleBuilderFilterChange}
              layout={builderConfig.layout}
              disabled={builderConfig.disabled}
              showPlaceholders={builderConfig.showPlaceholders}
              customLabels={{
                category: 'Item Category',
                quality: 'Item Quality',
                level: 'Required Level'
              }}
            />
            
            <div style={{ 
              marginTop: '16px', 
              padding: '12px',
              background: 'var(--color-surface-primary)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '12px',
              fontFamily: 'var(--font-family-mono)',
              color: 'var(--color-text-secondary)'
            }}>
              Current Values: {JSON.stringify(builderFilters, null, 2)}
            </div>
          </div>

          {/* Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Layout">
              <Select
                value={builderConfig.layout}
                onChange={(e) => handleBuilderConfigChange('layout', e.target.value)}
                options={[
                  { value: 'grid', label: 'Grid (Auto-sizing)' },
                  { value: 'horizontal', label: 'Horizontal (Inline)' },
                  { value: 'vertical', label: 'Vertical (Stacked)' }
                ]}
              />
            </FormField>

            <FormField label="Option Format">
              <Select
                value={builderConfig.optionFormat}
                onChange={(e) => handleBuilderConfigChange('optionFormat', e.target.value)}
                options={[
                  { value: 'array', label: 'Array Format' },
                  { value: 'object', label: 'Object Format (with icons)' }
                ]}
              />
            </FormField>

            <FormField label="State">
              <Select
                value={builderConfig.disabled ? 'disabled' : 'enabled'}
                onChange={(e) => handleBuilderConfigChange('disabled', e.target.value === 'disabled')}
                options={[
                  { value: 'enabled', label: 'Enabled' },
                  { value: 'disabled', label: 'Disabled' }
                ]}
              />
            </FormField>

            <FormField label="Placeholders">
              <Select
                value={builderConfig.showPlaceholders ? 'show' : 'hide'}
                onChange={(e) => handleBuilderConfigChange('showPlaceholders', e.target.value === 'show')}
                options={[
                  { value: 'show', label: 'Show Placeholders' },
                  { value: 'hide', label: 'Hide Placeholders' }
                ]}
              />
            </FormField>
          </div>

          {/* Code Example */}
          <div style={{ 
            background: 'var(--color-surface-primary)', 
            padding: '16px', 
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)', fontSize: '14px' }}>
              Code Example:
            </h4>
            <code style={{ 
              fontFamily: 'var(--font-family-mono)', 
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              display: 'block',
              whiteSpace: 'pre-wrap'
            }}>
{`<FilterSelectGroup
  filterOptions={{
    category: ${builderConfig.optionFormat === 'array' 
      ? "['Weapon', 'Armor', 'Accessory']" 
      : "{ weapon: 'Weapon ⚔️', armor: 'Armor 🛡️' }"},
    quality: ['Common', 'Rare', 'Epic'],
    level: [1, 5, 10, 15, 20]
  }}
  values={filterValues}
  onChange={handleFilterChange}
  layout="${builderConfig.layout}"${builderConfig.disabled ? '\n  disabled' : ''}${!builderConfig.showPlaceholders ? '\n  showPlaceholders={false}' : ''}
  customLabels={{
    category: 'Item Category',
    level: 'Required Level'
  }}
/>`}
            </code>
          </div>
        </div>
      </CardSection>

      {/* Common Use Cases */}
      <CardSection type="content" title="Common Use Cases">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>
              Game Data Filtering
            </h4>
            <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '16px' }}>
              Filter monsters, items, or game content by multiple criteria
            </p>
            <FilterSelectGroup
              filterOptions={{
                type: ['Monster', 'NPC', 'Boss', 'Pet'],
                location: ['Forest', 'Mountain', 'Desert', 'Ocean', 'Dungeon'],
                cr_rating: ['0-2', '3-5', '6-8', '9-12', '13-16', '17-20']
              }}
              values={{}}
              onChange={() => {}}
              customLabels={{
                cr_rating: 'Challenge Rating'
              }}
            />
          </div>

          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>
              Generation Queue Filtering
            </h4>
            <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '16px' }}>
              Filter generation tasks by status, type, and priority
            </p>
            <FilterSelectGroup
              filterOptions={{
                status: {
                  pending: 'Pending ⏳',
                  processing: 'Processing 🔄',
                  completed: 'Completed ✅',
                  failed: 'Failed ❌'
                },
                type: ['Monster', 'Lore', 'Item', 'Location'],
                priority: [1, 2, 3, 4, 5]
              }}
              values={{ status: 'pending' }}
              onChange={() => {}}
              layout="horizontal"
            />
          </div>

          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>
              User Preferences
            </h4>
            <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '16px' }}>
              Settings and preference selection
            </p>
            <div style={{ maxWidth: '400px' }}>
              <FilterSelectGroup
                filterOptions={{
                  theme: ['Dark', 'Light', 'Auto'],
                  language: ['English', 'Spanish', 'French', 'German'],
                  difficulty: ['Beginner', 'Intermediate', 'Advanced', 'Expert']
                }}
                values={{ theme: 'Dark', difficulty: 'Intermediate' }}
                onChange={() => {}}
                layout="vertical"
                showPlaceholders={false}
              />
            </div>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default FilterControlsExamples;