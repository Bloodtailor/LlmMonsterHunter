// ExplosionDemo - Showcase both ExplosionEngine (raw) and ExplosionPreset (high-level)
// Test the full flexibility of the modular explosion system

import React, { useState } from 'react';
import { ExplosionEngine, ExplosionPreset, EXPLOSION_TYPES } from '../shared/ui/primitives/Explosion/index.js';
import { COLOR_THEMES } from '../shared/constants/constants.js';
import color from '../shared/styles/color.js';

function ExplosionDemo() {
  const [activeTab, setActiveTab] = useState('preset'); // 'preset' or 'engine'
  
  // Preset configuration
  const [presetConfig, setPresetConfig] = useState({
    type: 'particle-storm',
    colorTheme: 'fire',
    size: 'md',
    intensity: 1,
    speed: 1,
    randomize: false
  });

  // Engine configuration
  const [engineConfig, setEngineConfig] = useState({
    particles: 20,
    streaks: 10,
    rings: 3,
    fragments: 5,
    waves: 2,
    sparks: 15,
    pattern: 'radial',
    hasFlash: true,
    hasShockwave: true,
    colors: ['#ff6b35', '#f7931e', '#ffd700'],
    size: 'md',
    intensity: 1,
    speed: 1
  });
  
  const [triggerKey, setTriggerKey] = useState(0);
  const [showColorPicker, setShowColorPicker] = useState(false);

  const explode = () => {
    setTriggerKey(prev => prev + 1);
  };

  const randomizePreset = () => {
    setPresetConfig(prev => ({ ...prev, randomize: true }));
    explode();
  };

  const randomizeEngine = () => {
    // Randomize some engine params, leave others to be auto-randomized
    setEngineConfig(prev => ({
      ...prev,
      particles: Math.random() > 0.5 ? Math.floor(Math.random() * 40) + 10 : null, // Sometimes let it randomize
      streaks: Math.random() > 0.5 ? Math.floor(Math.random() * 20) + 5 : null,
      rings: Math.random() > 0.5 ? Math.floor(Math.random() * 8) + 1 : null,
      fragments: Math.random() > 0.5 ? Math.floor(Math.random() * 15) : null,
      waves: Math.random() > 0.5 ? Math.floor(Math.random() * 6) : null,
      sparks: Math.random() > 0.5 ? Math.floor(Math.random() * 25) + 5 : null,
      colors: null // Let it generate random colors
    }));
    explode();
  };

  const updatePresetConfig = (key, value) => {
    setPresetConfig(prev => ({ ...prev, [key]: value, randomize: false }));
  };

  const updateEngineConfig = (key, value) => {
    setEngineConfig(prev => ({ ...prev, [key]: value }));
  };

  const copyCode = () => {
    let code;
    if (activeTab === 'preset') {
      if (presetConfig.randomize) {
        code = `<ExplosionPreset randomize={true} />`;
      } else {
        const props = [];
        if (presetConfig.type !== 'particle-storm') props.push(`type="${presetConfig.type}"`);
        if (presetConfig.colorTheme !== 'fire') props.push(`colorTheme="${presetConfig.colorTheme}"`);
        if (presetConfig.size !== 'md') props.push(`size="${presetConfig.size}"`);
        if (presetConfig.intensity !== 1) props.push(`intensity={${presetConfig.intensity}}`);
        if (presetConfig.speed !== 1) props.push(`speed={${presetConfig.speed}}`);
        
        code = `<ExplosionPreset${props.length ? '\n  ' + props.join('\n  ') + '\n' : ' '}/>`;
      }
    } else {
      // Engine code
      const props = [];
      if (engineConfig.particles !== null) props.push(`particles={${engineConfig.particles}}`);
      if (engineConfig.streaks !== null) props.push(`streaks={${engineConfig.streaks}}`);
      if (engineConfig.rings !== null) props.push(`rings={${engineConfig.rings}}`);
      if (engineConfig.fragments !== null) props.push(`fragments={${engineConfig.fragments}}`);
      if (engineConfig.waves !== null) props.push(`waves={${engineConfig.waves}}`);
      if (engineConfig.sparks !== null) props.push(`sparks={${engineConfig.sparks}}`);
      if (engineConfig.pattern !== 'radial') props.push(`pattern="${engineConfig.pattern}"`);
      if (!engineConfig.hasFlash) props.push(`hasFlash={false}`);
      if (!engineConfig.hasShockwave) props.push(`hasShockwave={false}`);
      if (engineConfig.colors) props.push(`colors={${JSON.stringify(engineConfig.colors)}}`);
      if (engineConfig.size !== 'md') props.push(`size="${engineConfig.size}"`);
      if (engineConfig.intensity !== 1) props.push(`intensity={${engineConfig.intensity}}`);
      if (engineConfig.speed !== 1) props.push(`speed={${engineConfig.speed}}`);
      
      code = `<ExplosionEngine${props.length ? '\n  ' + props.join('\n  ') + '\n' : ' '}/>`;
    }
    
    navigator.clipboard.writeText(code);
    alert('Code copied to clipboard!');
  };

  // Get all available colors organized by family
  const colorFamilies = color.getColorsByFamily();

  const currentConfig = activeTab === 'preset' ? presetConfig : engineConfig;
  const CurrentExplosion = activeTab === 'preset' ? ExplosionPreset : ExplosionEngine;

  return (
    <div style={{ 
      padding: '40px', 
      backgroundColor: '#1a1a2e', 
      minHeight: '100vh', 
      color: 'white',
      fontFamily: 'var(--font-family-primary)'
    }}>
      <h1 style={{ color: '#f39c12', marginBottom: '10px' }}>💥 Explosion System Demo</h1>
      <p style={{ color: '#b0b0b0', marginBottom: '40px' }}>
        Test both ExplosionPreset (easy presets) and ExplosionEngine (raw control)
      </p>

      {/* TAB SWITCHER */}
      <div style={{ marginBottom: '40px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', backgroundColor: '#16213e', borderRadius: '8px', padding: '4px' }}>
          <button
            onClick={() => setActiveTab('preset')}
            style={{
              padding: '12px 24px',
              backgroundColor: activeTab === 'preset' ? '#f39c12' : 'transparent',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            🎯 ExplosionPreset
          </button>
          <button
            onClick={() => setActiveTab('engine')}
            style={{
              padding: '12px 24px',
              backgroundColor: activeTab === 'engine' ? '#f39c12' : 'transparent',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            ⚙️ ExplosionEngine
          </button>
        </div>
      </div>

      {/* EXPLOSION SHOWCASE */}
      {activeTab === 'preset' && (
        <div style={{ marginBottom: '50px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
            <h2 style={{ color: '#4a90e2', margin: 0 }}>🎆 Preset Types Showcase</h2>
            <button
              onClick={explode}
              style={{
                padding: '12px 24px',
                backgroundColor: '#e74c3c',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '600'
              }}
            >
              💥 EXPLODE ALL!
            </button>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '20px' 
          }}>
            {Object.entries(EXPLOSION_TYPES).map(([name, type]) => (
              <div key={type} style={{ textAlign: 'center' }}>
                <h4 style={{ 
                  color: '#f39c12', 
                  marginBottom: '10px',
                  textTransform: 'capitalize'
                }}>
                  {name.replace('_', ' ').toLowerCase()}
                </h4>
                <div style={{
                  position: 'relative',
                  width: '120px',
                  height: '120px',
                  backgroundColor: '#2d3436',
                  margin: '0 auto 10px',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '2px solid #0f3460',
                  cursor: 'pointer'
                }}
                onClick={() => updatePresetConfig('type', type)}
                >
                  🎯
                  <ExplosionPreset
                    key={`${type}-${triggerKey}`}
                    type={type}
                    colorTheme="fire"
                    size="sm"
                    autoStart={triggerKey > 0}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 400px', 
        gap: '40px',
        alignItems: 'start'
      }}>
        
        {/* CONTROLS PANEL */}
        <div style={{ 
          backgroundColor: '#16213e', 
          padding: '30px', 
          borderRadius: '12px',
          border: '2px solid #0f3460'
        }}>
          
          {/* QUICK ACTIONS */}
          <div style={{ marginBottom: '30px', textAlign: 'center' }}>
            <h3 style={{ color: '#f39c12', marginBottom: '15px' }}>🎲 Quick Actions</h3>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              <button
                onClick={activeTab === 'preset' ? randomizePreset : randomizeEngine}
                style={{
                  padding: '12px 20px',
                  backgroundColor: '#e74c3c',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                🎲 RANDOMIZE
              </button>
              <button
                onClick={explode}
                style={{
                  padding: '12px 20px',
                  backgroundColor: '#27ae60',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                💥 EXPLODE
              </button>
            </div>
          </div>

          {/* PRESET CONTROLS */}
          {activeTab === 'preset' && (
            <>
              {/* EXPLOSION TYPE */}
              <div style={{ marginBottom: '25px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '10px', 
                  fontWeight: '600',
                  color: '#e0e0e0'
                }}>
                  Explosion Type
                </label>
                <select
                  value={presetConfig.type}
                  onChange={(e) => updatePresetConfig('type', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    backgroundColor: '#2d3436',
                    color: 'white',
                    border: '1px solid #0f3460',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                >
                  {Object.entries(EXPLOSION_TYPES).map(([name, type]) => (
                    <option key={type} value={type}>
                      {name.replace('_', ' ').toLowerCase()}
                    </option>
                  ))}
                </select>
              </div>

              {/* COLOR THEME */}
              <div style={{ marginBottom: '25px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '10px', 
                  fontWeight: '600',
                  color: '#e0e0e0'
                }}>
                  Color Theme
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '8px' }}>
                  {Object.entries(COLOR_THEMES).map(([name, theme]) => (
                    <button
                      key={name}
                      onClick={() => updatePresetConfig('colorTheme', name)}
                      style={{
                        padding: '8px',
                        backgroundColor: presetConfig.colorTheme === name ? '#f39c12' : '#2d3436',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        textTransform: 'capitalize'
                      }}
                    >
                      {name}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* ENGINE CONTROLS */}
          {activeTab === 'engine' && (
            <>
              {/* ELEMENT COUNTS */}
              <div style={{ marginBottom: '25px' }}>
                <h4 style={{ color: '#4a90e2', marginBottom: '15px' }}>Element Counts (null = randomized)</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
                  {['particles', 'streaks', 'rings', 'fragments', 'waves', 'sparks'].map(element => (
                    <div key={element}>
                      <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', color: '#e0e0e0', textTransform: 'capitalize' }}>
                        {element}: {engineConfig[element] || 'random'}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max={element === 'particles' ? 50 : element === 'sparks' ? 40 : 30}
                        value={engineConfig[element] || 0}
                        onChange={(e) => {
                          const val = parseInt(e.target.value);
                          updateEngineConfig(element, val === 0 ? null : val);
                        }}
                        style={{ width: '100%' }}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* PATTERN & EFFECTS */}
              <div style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', marginBottom: '10px', fontWeight: '600', color: '#e0e0e0' }}>
                  Pattern
                </label>
                <select
                  value={engineConfig.pattern}
                  onChange={(e) => updateEngineConfig('pattern', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#2d3436',
                    color: 'white',
                    border: '1px solid #0f3460',
                    borderRadius: '6px',
                    fontSize: '14px',
                    marginBottom: '15px'
                  }}
                >
                  <option value="radial">Radial</option>
                  <option value="lightning">Lightning</option>
                  <option value="implosion">Implosion</option>
                  <option value="spiral">Spiral</option>
                  <option value="dome">Dome</option>
                  <option value="chain">Chain</option>
                  <option value="shockwave">Shockwave</option>
                  <option value="shatter">Shatter</option>
                </select>

                <div style={{ display: 'flex', gap: '15px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                    <input
                      type="checkbox"
                      checked={engineConfig.hasFlash}
                      onChange={(e) => updateEngineConfig('hasFlash', e.target.checked)}
                      style={{ marginRight: '8px' }}
                    />
                    Flash
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                    <input
                      type="checkbox"
                      checked={engineConfig.hasShockwave}
                      onChange={(e) => updateEngineConfig('hasShockwave', e.target.checked)}
                      style={{ marginRight: '8px' }}
                    />
                    Shockwave
                  </label>
                </div>
              </div>

              {/* COLORS */}
              <div style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', marginBottom: '10px', fontWeight: '600', color: '#e0e0e0' }}>
                  Colors (current: {engineConfig.colors ? engineConfig.colors.length : 'random'})
                </label>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
                  {engineConfig.colors && engineConfig.colors.map((color, i) => (
                    <div key={i} style={{
                      width: '30px',
                      height: '30px',
                      backgroundColor: color,
                      borderRadius: '4px',
                      border: '2px solid #0f3460'
                    }} />
                  ))}
                </div>
                <button
                  onClick={() => updateEngineConfig('colors', null)}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#2d3436',
                    color: 'white',
                    border: '1px solid #0f3460',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  Use Random Colors
                </button>
              </div>
            </>
          )}

          {/* SHARED CONTROLS */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px', marginBottom: '25px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#e0e0e0' }}>
                Size
              </label>
              <select
                value={currentConfig.size}
                onChange={(e) => activeTab === 'preset' 
                  ? updatePresetConfig('size', e.target.value)
                  : updateEngineConfig('size', e.target.value)
                }
                style={{
                  width: '100%',
                  padding: '8px',
                  backgroundColor: '#2d3436',
                  color: 'white',
                  border: '1px solid #0f3460',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="sm">Small</option>
                <option value="md">Medium</option>
                <option value="lg">Large</option>
                <option value="xl">XL</option>
                <option value="massive">Massive</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#e0e0e0' }}>
                Intensity: {currentConfig.intensity}x
              </label>
              <input
                type="range"
                min="0.5"
                max="3"
                step="0.1"
                value={currentConfig.intensity}
                onChange={(e) => activeTab === 'preset' 
                  ? updatePresetConfig('intensity', parseFloat(e.target.value))
                  : updateEngineConfig('intensity', parseFloat(e.target.value))
                }
                style={{ width: '100%' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#e0e0e0' }}>
                Speed: {currentConfig.speed}x
              </label>
              <input
                type="range"
                min="0.5"
                max="3"
                step="0.1"
                value={currentConfig.speed}
                onChange={(e) => activeTab === 'preset' 
                  ? updatePresetConfig('speed', parseFloat(e.target.value))
                  : updateEngineConfig('speed', parseFloat(e.target.value))
                }
                style={{ width: '100%' }}
              />
            </div>
          </div>

          {/* COPY CODE */}
          <button
            onClick={copyCode}
            style={{
              width: '100%',
              padding: '15px',
              backgroundColor: '#4a90e2',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            📋 Copy {activeTab === 'preset' ? 'Preset' : 'Engine'} Code
          </button>
        </div>

        {/* PREVIEW AREA */}
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ marginBottom: '30px', color: '#4a90e2' }}>
            🎯 {activeTab === 'preset' ? 'ExplosionPreset' : 'ExplosionEngine'} Preview
          </h2>
          
          {/* Main Explosion Stage */}
          <div style={{
            position: 'relative',
            width: '300px',
            height: '300px',
            backgroundColor: '#2d3436',
            margin: '0 auto 30px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '3px solid #0f3460',
            fontSize: '24px',
            overflow: 'hidden'
          }}>
            🎯 TARGET
            <CurrentExplosion 
              key={triggerKey}
              {...currentConfig}
              autoStart={triggerKey > 0}
            />
          </div>

          {/* Current Config Display */}
          <div style={{
            backgroundColor: '#16213e',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #0f3460',
            marginBottom: '20px'
          }}>
            <h3 style={{ marginBottom: '15px', color: '#f39c12' }}>
              {activeTab === 'preset' ? '🎯 Preset Configuration' : '⚙️ Engine Configuration'}
            </h3>
            <div style={{ fontSize: '14px', textAlign: 'left' }}>
              {activeTab === 'preset' ? (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Type:</strong> {presetConfig.type.replace('-', ' ')}
                  </div>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Theme:</strong> {presetConfig.colorTheme}
                  </div>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Size:</strong> {presetConfig.size}
                  </div>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Intensity:</strong> {presetConfig.intensity}x
                  </div>
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', fontSize: '12px' }}>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Particles:</strong> {engineConfig.particles || 'random'}
                  </div>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Streaks:</strong> {engineConfig.streaks || 'random'}
                  </div>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Rings:</strong> {engineConfig.rings || 'random'}
                  </div>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Fragments:</strong> {engineConfig.fragments || 'random'}
                  </div>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Waves:</strong> {engineConfig.waves || 'random'}
                  </div>
                  <div style={{ color: '#e0e0e0' }}>
                    <strong>Sparks:</strong> {engineConfig.sparks || 'random'}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Code Preview */}
          <div style={{
            backgroundColor: '#16213e',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #0f3460'
          }}>
            <h4 style={{ color: '#f39c12', marginBottom: '10px' }}>Generated Code</h4>
            <pre style={{
              backgroundColor: '#0f3460',
              padding: '15px',
              borderRadius: '6px',
              textAlign: 'left',
              fontSize: '11px',
              color: '#e0e0e0',
              overflow: 'auto',
              whiteSpace: 'pre-wrap'
            }}>
              {/* Code preview will be generated by copyCode logic */}
              {activeTab === 'preset' ? (
                presetConfig.randomize ? '<ExplosionPreset randomize={true} />' : 
                `<ExplosionPreset${[
                  presetConfig.type !== 'particle-storm' ? `\n  type="${presetConfig.type}"` : '',
                  presetConfig.colorTheme !== 'fire' ? `\n  colorTheme="${presetConfig.colorTheme}"` : '',
                  presetConfig.size !== 'md' ? `\n  size="${presetConfig.size}"` : '',
                  presetConfig.intensity !== 1 ? `\n  intensity={${presetConfig.intensity}}` : '',
                  presetConfig.speed !== 1 ? `\n  speed={${presetConfig.speed}}` : ''
                ].filter(Boolean).join('') + '\n'}/>`
              ) : (
                `<ExplosionEngine${[
                  engineConfig.particles !== null ? `\n  particles={${engineConfig.particles}}` : '',
                  engineConfig.streaks !== null ? `\n  streaks={${engineConfig.streaks}}` : '',
                  engineConfig.rings !== null ? `\n  rings={${engineConfig.rings}}` : '',
                  engineConfig.fragments !== null ? `\n  fragments={${engineConfig.fragments}}` : '',
                  engineConfig.waves !== null ? `\n  waves={${engineConfig.waves}}` : '',
                  engineConfig.sparks !== null ? `\n  sparks={${engineConfig.sparks}}` : ''
                ].filter(Boolean).join('') + '\n'}/>`
              )}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ExplosionDemo;