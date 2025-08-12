// CoCaTok Examples Component - Showcase all CoCaTok variations
// Interactive examples and builder for Collectable Card Tokens
// Features 3D spinning cards with explosion effects

import React, { useState } from 'react';
import { 
  CoCaTok, 
  COCATOK_SIZES 
} from '../../shared/ui/CoCaTok/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';
import { Alert } from '../../shared/ui/Feedback/index.js';
import BasicColorSelection from '../../shared/ui/ColorSelection/BasicColorSelection.js';

function CoCaTokExamples() {
  // Interactive builder state
  const [builderState, setBuilderState] = useState({
    color: 'purple-mystic',
    size: 'md',
    emoji: '✨',
    disabled: false
  });

  // Track exploded cards (cards that have been activated disappear forever)
  const [explodedCards, setExplodedCards] = useState(new Set());

  // Popular emoji options for the builder
  const emojiOptions = [
    { value: '✨', label: '✨ Sparkles' },
    { value: '🔥', label: '🔥 Fire' },
    { value: '⚡', label: '⚡ Lightning' },
    { value: '💎', label: '💎 Diamond' },
    { value: '🌟', label: '🌟 Star' },
    { value: '🎯', label: '🎯 Target' },
    { value: '🚀', label: '🚀 Rocket' },
    { value: '👑', label: '👑 Crown' },
    { value: '🗿', label: '🗿 Moai' },
    { value: '🐲', label: '🐲 Dragon' },
    { value: '🦄', label: '🦄 Unicorn' },
    { value: '🌈', label: '🌈 Rainbow' },
    { value: '🔮', label: '🔮 Crystal Ball' },
    { value: '⚔️', label: '⚔️ Crossed Swords' },
    { value: '🛡️', label: '🛡️ Shield' }
  ];

  // Sample color variations for demonstrations
  const colorExamples = [
    'red-intense', 'orange-vibrant', 'yellow-bright', 'green-electric',
    'blue-electric', 'purple-mystic', 'pink-vibrant', 'white-pure'
  ];

  const handleBuilderChange = (field, value) => {
    setBuilderState(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleColorChange = (event, colorObj) => {
    if (colorObj) {
      handleBuilderChange('color', colorObj.name);
    }
  };

  const handleCardActivation = (cardId, color, emoji) => {
    console.log(`Card activated: ${cardId} (${color} ${emoji})`);
    setExplodedCards(prev => new Set([...prev, cardId]));
  };

  const resetExplodedCards = () => {
    setExplodedCards(new Set());
  };

  return (
    <Card size="lg" padding="lg" className="cocatok-examples">
      <CardSection type="header" title="CoCaTok Components Showcase" />
      
      {/* Introduction */}
      <CardSection type="content">
        <Alert type="info" size="sm">
          <strong>CoCaToks</strong> are interactive 3D spinning collectible card tokens. 
          They bounce gently, face you on hover, and explode dramatically when clicked - disappearing forever!
          Each card uses hue-based explosion effects matching its color theme.
        </Alert>
      </CardSection>

      {/* Size Variations */}
      <CardSection type="content" title="Size Variations">
        <div style={{ 
          display: 'flex', 
          gap: '24px', 
          alignItems: 'flex-start', 
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          {Object.values(COCATOK_SIZES).map(size => (
            <div key={`size-${size}`} style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong style={{ fontSize: '14px', color: 'var(--color-text-primary)' }}>
                  {size.toUpperCase()}
                </strong>
              </div>
              {!explodedCards.has(`size-${size}`) ? (
                <CoCaTok
                  color="purple-mystic"
                  size={size}
                  emoji="✨"
                  onActivate={(color, emoji) => handleCardActivation(`size-${size}`, color, emoji)}
                />
              ) : (
                <div style={{ 
                  width: size === 'sm' ? '70px' : size === 'md' ? '108px' : size === 'lg' ? '154px' : '156px',
                  height: size === 'sm' ? '94px' : size === 'md' ? '144px' : size === 'lg' ? '205px' : '208px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: 0.3,
                  fontSize: '12px',
                  color: 'var(--color-text-muted)'
                }}>
                  💥 Exploded!
                </div>
              )}
            </div>
          ))}
        </div>
      </CardSection>

      {/* Color Variations */}
      <CardSection type="content" title="Color Variations">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
          gap: '24px',
          justifyItems: 'center'
        }}>
          {colorExamples.map(color => (
            <div key={`color-${color}`} style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong style={{ fontSize: '12px', color: 'var(--color-text-primary)' }}>
                  {color.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </strong>
              </div>
              {!explodedCards.has(`color-${color}`) ? (
                <CoCaTok
                  color={color}
                  size="sm"
                  emoji="🔥"
                  onActivate={(colorVal, emoji) => handleCardActivation(`color-${color}`, colorVal, emoji)}
                />
              ) : (
                <div style={{ 
                  width: '70px',
                  height: '94px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: 0.3,
                  fontSize: '10px',
                  color: 'var(--color-text-muted)'
                }}>
                  💥
                </div>
              )}
            </div>
          ))}
        </div>
      </CardSection>

      {/* Emoji Variations */}
      <CardSection type="content" title="Emoji Variations">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', 
          gap: '16px',
          justifyItems: 'center'
        }}>
          {['⚡', '💎', '🌟', '🐲', '🔮', '👑', '🚀', '🛡️'].map(emoji => (
            <div key={`emoji-${emoji}`} style={{ textAlign: 'center' }}>
              {!explodedCards.has(`emoji-${emoji}`) ? (
                <CoCaTok
                  color="blue-electric"
                  size="sm"
                  emoji={emoji}
                  onActivate={(color, emojiVal) => handleCardActivation(`emoji-${emoji}`, color, emojiVal)}
                />
              ) : (
                <div style={{ 
                  width: '70px',
                  height: '94px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: 0.3,
                  fontSize: '10px',
                  color: 'var(--color-text-muted)'
                }}>
                  💥
                </div>
              )}
            </div>
          ))}
        </div>
      </CardSection>

      {/* States Showcase */}
      <CardSection type="content" title="Special States">
        <div style={{ 
          display: 'flex', 
          gap: '24px', 
          alignItems: 'center', 
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: '8px' }}>
              <strong style={{ fontSize: '14px', color: 'var(--color-text-primary)' }}>
                Normal
              </strong>
            </div>
            {!explodedCards.has('state-normal') ? (
              <CoCaTok
                color="green-electric"
                size="md"
                emoji="🌟"
                onActivate={(color, emoji) => handleCardActivation('state-normal', color, emoji)}
              />
            ) : (
              <div style={{ 
                width: '108px',
                height: '144px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: 0.3,
                fontSize: '12px',
                color: 'var(--color-text-muted)'
              }}>
                💥 Exploded!
              </div>
            )}
          </div>

          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: '8px' }}>
              <strong style={{ fontSize: '14px', color: 'var(--color-text-primary)' }}>
                Disabled
              </strong>
            </div>
            <CoCaTok
              color="gray-medium"
              size="md"
              emoji="🚫"
              disabled={true}
            />
          </div>
        </div>
      </CardSection>

      {/* Reset Button */}
      {explodedCards.size > 0 && (
        <CardSection type="content">
          <div style={{ textAlign: 'center' }}>
            <button
              onClick={resetExplodedCards}
              style={{
                background: 'var(--primary-color)',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 'var(--font-weight-medium)'
              }}
            >
              🔄 Reset All Exploded Cards ({explodedCards.size})
            </button>
          </div>
        </CardSection>
      )}

      {/* Interactive Builder */}
      <CardSection type="content" title="Build Your Own CoCaTok (BYOC)">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '32px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            textAlign: 'center',
            border: '2px dashed var(--color-text-muted)',
            minHeight: '200px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '16px'
          }}>
            <h4 style={{ margin: 0, color: 'var(--color-text-primary)' }}>Your Custom CoCaTok</h4>
            
            {!explodedCards.has('builder-preview') ? (
              <CoCaTok
                color={builderState.color}
                size={builderState.size}
                emoji={builderState.emoji}
                disabled={builderState.disabled}
                onActivate={(color, emoji) => handleCardActivation('builder-preview', color, emoji)}
              />
            ) : (
              <div style={{ 
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '12px',
                opacity: 0.6
              }}>
                <div style={{ fontSize: '48px' }}>💥</div>
                <div style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>
                  Your CoCaTok exploded! Change any setting to create a new one.
                </div>
              </div>
            )}
          </div>

          {/* Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Color">
              <BasicColorSelection
                value={builderState.color}
                onChange={handleColorChange}
                placeholder="Select a color..."
                showPreview={true}
              />
            </FormField>

            <FormField label="Size">
              <Select
                value={builderState.size}
                onChange={(e) => handleBuilderChange('size', e.target.value)}
                options={Object.values(COCATOK_SIZES).map(size => ({
                  value: size,
                  label: size.toUpperCase()
                }))}
              />
            </FormField>

            <FormField label="Emoji">
              <Select
                value={builderState.emoji}
                onChange={(e) => handleBuilderChange('emoji', e.target.value)}
                options={emojiOptions}
              />
            </FormField>

            <FormField label="State">
              <Select
                value={builderState.disabled ? 'disabled' : 'normal'}
                onChange={(e) => handleBuilderChange('disabled', e.target.value === 'disabled')}
                options={[
                  { value: 'normal', label: 'Normal (Interactive)' },
                  { value: 'disabled', label: 'Disabled' }
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
              {`<CoCaTok
  color="${builderState.color}"
  size="${builderState.size}"
  emoji="${builderState.emoji}"
  ${builderState.disabled ? 'disabled={true}' : ''}
  onActivate={(color, emoji) => {
    console.log('Card exploded!', color, emoji);
    // Handle card activation - maybe add to inventory?
  }}
/>`}
            </code>
          </div>

          {/* Usage Tips */}
          <div style={{ 
            background: 'var(--color-surface-secondary)', 
            padding: '16px', 
            borderRadius: 'var(--radius-md)',
            fontSize: '14px',
            color: 'var(--color-text-secondary)'
          }}>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--color-text-primary)' }}>
              💡 CoCaTok Usage Tips:
            </h4>
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              <li>Cards automatically bounce and spin when idle</li>
              <li>Hover to make them face you with smooth animation</li>
              <li>Click to trigger explosion effect and disappear forever</li>
              <li>Each color creates themed explosion effects (red = fire, blue = ice, etc.)</li>
              <li>Perfect for rare collectibles found in dungeons</li>
              <li>Use <code>onActivate</code> to handle collection/inventory logic</li>
            </ul>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

// Reset exploded cards when color/emoji/size changes
function usePrevious(value) {
  const ref = React.useRef();
  React.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export default CoCaTokExamples;