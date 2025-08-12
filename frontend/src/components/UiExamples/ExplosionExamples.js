// Explosion Examples Component - Showcase all Explosion component variations
// Interactive examples and builder for ExplosionPreset, HueBasedExplosion, and ExplosionEngine
// Clickable cards to trigger explosions one at a time

import React, { useState } from 'react';
import { 
  ExplosionPreset,
  HueBasedExplosion,
  ExplosionEngine,
  EXPLOSION_TYPES,
  SIZE_MULTIPLIERS,
  EXPLOSION_PATTERNS
} from '../../shared/ui/Explosion/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';
import { Button } from '../../shared/ui/Button/index.js';
import BasicColorSelection from '../../shared/ui/ColorSelection/BasicColorSelection.js';
import { COLOR_THEMES } from '../../shared/constants/constants.js';
import { getHueNames } from '../../shared/styles/color.js';

function ExplosionExamples() {
  // Track which explosions are currently active
  const [activeExplosions, setActiveExplosions] = useState(new Set());
  
  // Interactive builder state
  const [explosionBuilder, setExplExplosionBuilder] = useState({
    component: 'preset', // 'preset', 'hue', 'engine'
    // Preset options
    type: 'particle-storm',
    colorTheme: 'fire',
    // Hue options
    hue: 'red',
    // Engine options (for advanced)
    particles: 16,
    streaks: 8,
    rings: 2,
    pattern: 'radial',
    // Common options
    size: 'md',
    intensity: 1,
    speed: 1,
    // Color selection
    selectedColor: 'red-intense'
  });

  const handleBuilderChange = (field, value) => {
    setExplExplosionBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle explosion trigger
  const triggerExplosion = (explosionId) => {
    setActiveExplosions(prev => new Set([...prev, explosionId]));
  };

  // Handle explosion completion
  const onExplosionComplete = (explosionId) => {
    setActiveExplosions(prev => {
      const newSet = new Set(prev);
      newSet.delete(explosionId);
      return newSet;
    });
  };

  // Render builder explosion
  const renderBuilderExplosion = () => {
    const explosionId = 'builder-explosion';
    const isActive = activeExplosions.has(explosionId);
    
    const commonProps = {
      size: explosionBuilder.size,
      intensity: explosionBuilder.intensity,
      speed: explosionBuilder.speed,
      autoStart: isActive,
      onComplete: () => onExplosionComplete(explosionId)
    };

    if (explosionBuilder.component === 'hue') {
      return (
        <HueBasedExplosion
          hue={explosionBuilder.hue}
          {...commonProps}
        />
      );
    } else if (explosionBuilder.component === 'engine') {
      return (
        <ExplosionEngine
          particles={explosionBuilder.particles}
          streaks={explosionBuilder.streaks}
          rings={explosionBuilder.rings}
          pattern={explosionBuilder.pattern}
          {...commonProps}
        />
      );
    } else {
      return (
        <ExplosionPreset
          type={explosionBuilder.type}
          colorTheme={explosionBuilder.colorTheme}
          {...commonProps}
        />
      );
    }
  };

  return (
    <Card size="lg" padding="lg" className="explosion-examples">
      <CardSection type="header" title="Explosion Components Showcase" />
      
      {/* Explosion Type Presets */}
      <CardSection type="content" title="Explosion Types (Click to Explode!)">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
          gap: '16px' 
        }}>
          {Object.values(EXPLOSION_TYPES).map(type => {
            const explosionId = `preset-${type}`;
            const isActive = activeExplosions.has(explosionId);
            
            return (
              <Card
                key={type}
                variant="elevated"
                size="sm"
                padding="none"
                interactive
                onClick={() => triggerExplosion(explosionId)}
                style={{ 
                  position: 'relative',
                  width: '150px',
                  height: '150px',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  cursor: 'pointer',
                  background: 'var(--color-surface-secondary)',
                  border: isActive 
                    ? '3px solid var(--primary-color)' 
                    : '3px dashed var(--color-text-muted)'
                }}
                title={type.replace('-', ' ')}
              >
                {!isActive && (
                  <div style={{ textAlign: 'center', zIndex: 2, opacity: 0.7 }}>
                    <div style={{ 
                      fontSize: '16px', 
                      color: 'var(--color-text-primary)',
                      marginBottom: '4px',
                      textTransform: 'capitalize'
                    }}>
                      {type.replace('-', ' ')}
                    </div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: 'var(--color-text-muted)' 
                    }}>
                      Click to Test
                    </div>
                  </div>
                )}
                
                {/* Explosion overlay */}
                {isActive && (
                  <div style={{ 
                    position: 'absolute', 
                    top: '50%', 
                    left: '50%', 
                    transform: 'translate(-50%, -50%)',
                    zIndex: 1
                  }}>
                    <ExplosionPreset
                      type={type}
                      colorTheme="fire"
                      size="md"
                      autoStart={true}
                      onComplete={() => onExplosionComplete(explosionId)}
                    />
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </CardSection>

      {/* Size Variations */}
      <CardSection type="content" title="Size Variations">
        <div style={{ 
          display: 'flex', 
          gap: '16px',
          justifyContent: 'center',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          {Object.keys(SIZE_MULTIPLIERS).map(size => {
            const explosionId = `size-${size}`;
            const isActive = activeExplosions.has(explosionId);
            
            // Card size scales with explosion size
            const cardSizes = {
              sm: 80,
              md: 120,
              lg: 160,
              xl: 200,
              massive: 240
            };
            const cardSize = cardSizes[size] || 120;
            
            return (
              <Card
                key={size}
                variant="outlined"
                size="sm"
                padding="none"
                interactive
                onClick={() => triggerExplosion(explosionId)}
                style={{ 
                  position: 'relative',
                  width: `${cardSize}px`,
                  height: `${cardSize}px`,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  cursor: 'pointer',
                  background: 'var(--color-surface-secondary)',
                  border: isActive 
                    ? '3px solid var(--primary-color)' 
                    : '3px dashed var(--color-text-muted)'
                }}
                title={`${size.toUpperCase()} (${SIZE_MULTIPLIERS[size]}x)`}
              >
                {!isActive && (
                  <div style={{ textAlign: 'center', zIndex: 2, opacity: 0.7 }}>
                    <div style={{ 
                      fontSize: size === 'sm' ? '12px' : size === 'massive' ? '20px' : '16px', 
                      color: 'var(--color-text-primary)',
                      marginBottom: '4px'
                    }}>
                      {size.toUpperCase()}
                    </div>
                    <div style={{ 
                      fontSize: size === 'sm' ? '10px' : size === 'massive' ? '14px' : '12px', 
                      color: 'var(--color-text-muted)' 
                    }}>
                      {SIZE_MULTIPLIERS[size]}x
                    </div>
                  </div>
                )}
                
                {isActive && (
                  <div style={{ 
                    position: 'absolute', 
                    top: '50%', 
                    left: '50%', 
                    transform: 'translate(-50%, -50%)',
                    zIndex: 1
                  }}>
                    <ExplosionPreset
                      type="particle-storm"
                      colorTheme="rainbow"
                      size={size}
                      autoStart={true}
                      onComplete={() => onExplosionComplete(explosionId)}
                    />
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </CardSection>

      {/* Hue-Based Explosions */}
      <CardSection type="content" title="Color Hue Explosions">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
          gap: '12px' 
        }}>
          {getHueNames().slice(0, 8).map(hue => {
            const explosionId = `hue-${hue}`;
            const isActive = activeExplosions.has(explosionId);
            
            return (
              <Card
                key={hue}
                variant="default"
                size="sm"
                padding="none"
                interactive
                onClick={() => triggerExplosion(explosionId)}
                style={{ 
                  position: 'relative',
                  width: '120px',
                  height: '120px',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  cursor: 'pointer',
                  background: 'var(--color-surface-secondary)',
                  border: isActive 
                    ? '3px solid var(--primary-color)' 
                    : '3px dashed var(--color-text-muted)'
                }}
                title={hue.charAt(0).toUpperCase() + hue.slice(1)}
              >
                {!isActive && (
                  <div style={{ textAlign: 'center', zIndex: 2, opacity: 0.7 }}>
                    <div style={{ 
                      fontSize: '16px', 
                      color: 'var(--color-text-primary)',
                      marginBottom: '4px',
                      textTransform: 'capitalize'
                    }}>
                      {hue}
                    </div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: 'var(--color-text-muted)' 
                    }}>
                      Hue
                    </div>
                  </div>
                )}
                
                {isActive && (
                  <div style={{ 
                    position: 'absolute', 
                    top: '50%', 
                    left: '50%', 
                    transform: 'translate(-50%, -50%)',
                    zIndex: 1
                  }}>
                    <HueBasedExplosion
                      hue={hue}
                      size="sm"
                      intensity={1.2}
                      autoStart={true}
                      onComplete={() => onExplosionComplete(explosionId)}
                    />
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </CardSection>

      {/* Interactive Builder */}
      <CardSection type="content" title="Build Your Own Explosion">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-start' }}>
            
            {/* Explosion Test Area */}
            <Card 
              variant="elevated"
              size="md"
              padding="none"
              interactive
              onClick={() => triggerExplosion('builder-explosion')}
              style={{ 
                position: 'relative',
                width: '250px',
                height: '250px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                cursor: 'pointer',
                background: 'var(--color-surface-secondary)',
                border: activeExplosions.has('builder-explosion') 
                  ? '3px solid var(--primary-color)' 
                  : '3px dashed var(--color-text-muted)'
              }}
              title="Click to test your custom explosion"
            >
              {!activeExplosions.has('builder-explosion') && (
                <div style={{ textAlign: 'center', zIndex: 2, opacity: 0.7 }}>
                  <div style={{ 
                    fontSize: '18px', 
                    color: 'var(--color-text-primary)',
                    marginBottom: '8px'
                  }}>
                    🎆
                  </div>
                  <div style={{ 
                    fontSize: '14px', 
                    color: 'var(--color-text-muted)' 
                  }}>
                    Click to Test
                  </div>
                </div>
              )}
              
              {activeExplosions.has('builder-explosion') && (
                <div style={{ 
                  position: 'absolute', 
                  top: '50%', 
                  left: '50%', 
                  transform: 'translate(-50%, -50%)',
                  zIndex: 1
                }}>
                  {renderBuilderExplosion()}
                </div>
              )}
            </Card>

            {/* Quick Controls */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <FormField label="Component Type">
                <Select
                  value={explosionBuilder.component}
                  onChange={(e) => handleBuilderChange('component', e.target.value)}
                  options={[
                    { value: 'preset', label: 'Explosion Preset' },
                    { value: 'hue', label: 'Hue-Based' },
                    { value: 'engine', label: 'Raw Engine' }
                  ]}
                />
              </FormField>

              <FormField label="Size">
                <Select
                  value={explosionBuilder.size}
                  onChange={(e) => handleBuilderChange('size', e.target.value)}
                  options={Object.keys(SIZE_MULTIPLIERS).map(size => ({
                    value: size,
                    label: size.toUpperCase()
                  }))}
                />
              </FormField>

              <Button
                variant="secondary"
                size="sm"
                onClick={() => triggerExplosion('builder-explosion')}
                disabled={activeExplosions.has('builder-explosion')}
              >
                🎆 Trigger Explosion
              </Button>
            </div>
          </div>

          {/* Detailed Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            
            {/* Preset Controls */}
            {explosionBuilder.component === 'preset' && (
              <>
                <FormField label="Explosion Type">
                  <Select
                    value={explosionBuilder.type}
                    onChange={(e) => handleBuilderChange('type', e.target.value)}
                    options={Object.values(EXPLOSION_TYPES).map(type => ({
                      value: type,
                      label: type.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
                    }))}
                  />
                </FormField>

                <FormField label="Color Theme">
                  <Select
                    value={explosionBuilder.colorTheme}
                    onChange={(e) => handleBuilderChange('colorTheme', e.target.value)}
                    options={[
                      ...Object.keys(COLOR_THEMES).map(theme => ({
                        value: theme,
                        label: theme.charAt(0).toUpperCase() + theme.slice(1)
                      })),
                      ...getHueNames().map(hue => ({
                        value: hue,
                        label: `${hue.charAt(0).toUpperCase() + hue.slice(1)} Hue`
                      }))
                    ]}
                  />
                </FormField>
              </>
            )}

            {/* Hue Controls */}
            {explosionBuilder.component === 'hue' && (
              <FormField label="Color Hue">
                <Select
                  value={explosionBuilder.hue}
                  onChange={(e) => handleBuilderChange('hue', e.target.value)}
                  options={getHueNames().map(hue => ({
                    value: hue,
                    label: hue.charAt(0).toUpperCase() + hue.slice(1)
                  }))}
                />
              </FormField>
            )}

            {/* Engine Controls */}
            {explosionBuilder.component === 'engine' && (
              <>
                <FormField label="Particles">
                  <Select
                    value={explosionBuilder.particles}
                    onChange={(e) => handleBuilderChange('particles', parseInt(e.target.value))}
                    options={[0, 5, 10, 16, 25, 35, 50].map(num => ({
                      value: num,
                      label: num.toString()
                    }))}
                  />
                </FormField>

                <FormField label="Streaks">
                  <Select
                    value={explosionBuilder.streaks}
                    onChange={(e) => handleBuilderChange('streaks', parseInt(e.target.value))}
                    options={[0, 3, 8, 12, 20, 30].map(num => ({
                      value: num,
                      label: num.toString()
                    }))}
                  />
                </FormField>

                <FormField label="Rings">
                  <Select
                    value={explosionBuilder.rings}
                    onChange={(e) => handleBuilderChange('rings', parseInt(e.target.value))}
                    options={[0, 1, 2, 5, 8, 12].map(num => ({
                      value: num,
                      label: num.toString()
                    }))}
                  />
                </FormField>

                <FormField label="Pattern">
                  <Select
                    value={explosionBuilder.pattern}
                    onChange={(e) => handleBuilderChange('pattern', e.target.value)}
                    options={Object.values(EXPLOSION_PATTERNS).map(pattern => ({
                      value: pattern,
                      label: pattern.charAt(0).toUpperCase() + pattern.slice(1)
                    }))}
                  />
                </FormField>
              </>
            )}

            {/* Common Controls */}
            <FormField label="Intensity">
              <Select
                value={explosionBuilder.intensity}
                onChange={(e) => handleBuilderChange('intensity', parseFloat(e.target.value))}
                options={[0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5].map(num => ({
                  value: num,
                  label: `${num}x`
                }))}
              />
            </FormField>

            <FormField label="Speed">
              <Select
                value={explosionBuilder.speed}
                onChange={(e) => handleBuilderChange('speed', parseFloat(e.target.value))}
                options={[0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0].map(num => ({
                  value: num,
                  label: `${num}x`
                }))}
              />
            </FormField>

            {/* Color Selection */}
            <FormField label="Custom Color">
              <BasicColorSelection
                value={explosionBuilder.selectedColor}
                onChange={(event, colorObj) => {
                  handleBuilderChange('selectedColor', colorObj?.name || '');
                  if (colorObj && explosionBuilder.component === 'hue') {
                    // Extract hue from color name for hue-based explosions
                    const hue = colorObj.name.split('-')[0];
                    handleBuilderChange('hue', hue);
                  }
                }}
                placeholder="Select explosion color..."
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
              {(() => {
                if (explosionBuilder.component === 'hue') {
                  return `<HueBasedExplosion
  hue="${explosionBuilder.hue}"
  size="${explosionBuilder.size}"
  intensity={${explosionBuilder.intensity}}
  speed={${explosionBuilder.speed}}
  autoStart={false}
  onComplete={() => console.log('Explosion complete!')}
/>`;
                } else if (explosionBuilder.component === 'engine') {
                  return `<ExplosionEngine
  particles={${explosionBuilder.particles}}
  streaks={${explosionBuilder.streaks}}
  rings={${explosionBuilder.rings}}
  pattern="${explosionBuilder.pattern}"
  size="${explosionBuilder.size}"
  intensity={${explosionBuilder.intensity}}
  speed={${explosionBuilder.speed}}
  autoStart={false}
  onComplete={() => console.log('Explosion complete!')}
/>`;
                } else {
                  return `<ExplosionPreset
  type="${explosionBuilder.type}"
  colorTheme="${explosionBuilder.colorTheme}"
  size="${explosionBuilder.size}"
  intensity={${explosionBuilder.intensity}}
  speed={${explosionBuilder.speed}}
  autoStart={false}
  onComplete={() => console.log('Explosion complete!')}
/>`;
                }
              })()}
            </code>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default ExplosionExamples;