// Monster Card Component - WITH INTEGRATED PARTY TOGGLE BUTTON
// Front: Monster art + basic info, Back: Detailed stats and abilities
// Now includes party toggle button positioned relative to the card itself

import React, { useState } from 'react';
import FlippableCard from '../ui/FlippableCard';
import CardArtViewer from '../ui/CardArtViewer';

function MonsterCard({ 
  monster, 
  size = 'normal', 
  onAbilityGenerate = null,
  // Party toggle props
  showPartyToggle = false,
  isInParty = false,
  isPartyFull = false,
  onPartyToggle = null,
  partyDisabled = false
}) {
  const [generatingAbility, setGeneratingAbility] = useState(false);
  const [showArtViewer, setShowArtViewer] = useState(false);

  // Handle card art - use actual backend URL if available
  const getCardArtUrl = () => {
    if (monster.card_art?.exists && monster.card_art?.relative_path) {
      // Use the backend API endpoint to serve the image
      return `http://localhost:5000/api/monsters/card-art/${monster.card_art.relative_path}`;
    }
    return null; // Use placeholder
  };

  const handleAbilityGenerate = async () => {
    if (!onAbilityGenerate || generatingAbility) return;
    
    setGeneratingAbility(true);
    try {
      await onAbilityGenerate(monster.id);
    } finally {
      setGeneratingAbility(false);
    }
  };

  // Handle party toggle
  const handlePartyToggle = (e) => {
    e.stopPropagation(); // Prevent card flip
    if (onPartyToggle && !partyDisabled) {
      onPartyToggle(monster, isInParty);
    }
  };

  // Get party button state
  const getPartyButtonState = () => {
    if (partyDisabled) {
      return {
        icon: '⏳',
        className: 'party-toggle-disabled',
        title: 'Updating party...'
      };
    }
    
    if (isInParty) {
      return {
        icon: '✓',
        className: 'party-toggle-remove',
        title: `Remove ${monster.name} from party`
      };
    }
    
    if (isPartyFull) {
      return {
        icon: '🚫',
        className: 'party-toggle-full',
        title: 'Party is full (4/4)'
      };
    }
    
    return {
      icon: '+',
      className: 'party-toggle-add',
      title: `Add ${monster.name} to party`
    };
  };

  const getAbilityTypeIcon = (type) => {
    const icons = {
      attack: '⚔️',
      defense: '🛡️',
      support: '💚',
      special: '✨',
      movement: '💨',
      utility: '🔧'
    };
    return icons[type] || '⚡';
  };

  // Handle expand button click
  const handleExpandArt = (e) => {
    e.stopPropagation(); // Prevent card flip
    if (getCardArtUrl()) {
      setShowArtViewer(true);
    }
  };

  // Front of card - Art + Basic Info
  const frontContent = (
    <div className="monster-card-front">
      {/* Party Toggle Button - positioned relative to card */}
      {showPartyToggle && (
        <button
          className={`party-toggle-button ${getPartyButtonState().className}`}
          onClick={handlePartyToggle}
          disabled={partyDisabled || (isPartyFull && !isInParty)}
          title={getPartyButtonState().title}
        >
          {getPartyButtonState().icon}
        </button>
      )}

      {/* Card Art */}
      <div className="monster-art-section">
        {getCardArtUrl() ? (
          <>
            <img 
              src={getCardArtUrl()} 
              alt={`${monster.name} card art`}
              className="monster-art"
            />
            {/* Expand Button */}
            <button 
              className="expand-art-button"
              onClick={handleExpandArt}
              title="View full-size card art"
            >
              🔍
            </button>
          </>
        ) : (
          <div className="monster-art-placeholder">
            <div className="placeholder-icon">🐲</div>
            <span className="placeholder-text">
              {monster.card_art?.exists ? 'Loading...' : 'No Card Art'}
            </span>
          </div>
        )}
      </div>

      {/* Basic Info Overlay */}
      <div className="monster-info-overlay">
        <div className="monster-header">
          <h3 className="monster-name">{monster.name}</h3>
          <span className="monster-species">{monster.species}</span>
        </div>

        {/* Ability Preview - Hide for small cards */}
        {size !== 'small' && (
          <div className="abilities-preview">
            <span className="abilities-count">⚡ {monster.ability_count} abilities</span>
            {monster.abilities && monster.abilities.length > 0 && (
              <div className="ability-chips">
                {monster.abilities.slice(0, 2).map((ability, index) => (
                  <span key={index} className="ability-chip">
                    {getAbilityTypeIcon(ability.ability_type)} {ability.name}
                  </span>
                ))}
                {monster.abilities.length > 2 && (
                  <span className="more-abilities">+{monster.abilities.length - 2}</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  // Back of card - Detailed Info
  const backContent = (
    <div className="monster-card-back">
      {/* Header */}
      <div className="detail-header">
        <h3>{monster.name}</h3>
        <span className="species-badge">{monster.species}</span>
      </div>

      {/* Description */}
      <div className="description-section">
        <p className="monster-description">{monster.description}</p>
      </div>

      {/* Backstory */}
      {monster.backstory && (
        <div className="backstory-section">
          <h4>📖 Backstory</h4>
          <p className="monster-backstory">{monster.backstory}</p>
        </div>
      )}

      {/* Stats Grid */}
      <div className="stats-section">
        <h4>Stats</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-name">Health</span>
            <span className="stat-bar">
              <div className="stat-fill" style={{width: `${(monster.stats.current_health / monster.stats.max_health) * 100}%`}}></div>
              <span className="stat-text">{monster.stats.current_health}/{monster.stats.max_health}</span>
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-name">Attack</span>
            <span className="stat-number">{monster.stats.attack}</span>
          </div>
          <div className="stat-item">
            <span className="stat-name">Defense</span>
            <span className="stat-number">{monster.stats.defense}</span>
          </div>
          <div className="stat-item">
            <span className="stat-name">Speed</span>
            <span className="stat-number">{monster.stats.speed}</span>
          </div>
        </div>
      </div>

      {/* Abilities Section */}
      <div className="abilities-section">
        <div className="abilities-header">
          <h4>Abilities ({monster.ability_count})</h4>
          {onAbilityGenerate && (
            <button 
              onClick={handleAbilityGenerate}
              disabled={generatingAbility}
              className="add-ability-btn"
            >
              {generatingAbility ? '🔄' : '✨'}
            </button>
          )}
        </div>
        
        <div className="abilities-list">
          {monster.abilities && monster.abilities.length > 0 ? (
            monster.abilities.map((ability, index) => (
              <div key={index} className="ability-detail">
                <div className="ability-name">
                  {getAbilityTypeIcon(ability.ability_type)} {ability.name}
                </div>
                <div className="ability-description">{ability.description}</div>
              </div>
            ))
          ) : (
            <div className="no-abilities">
              <p>No abilities yet</p>
              <p>Generate some abilities!</p>
            </div>
          )}
        </div>
      </div>

      {/* Personality Traits */}
      {monster.personality_traits && monster.personality_traits.length > 0 && (
        <div className="traits-section">
          <h4>Personality</h4>
          <div className="traits-list">
            {monster.personality_traits.map((trait, index) => (
              <span key={index} className="trait-tag">{trait}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <>
      <FlippableCard
        frontContent={frontContent}
        backContent={backContent}
        cardId={monster.id}
        className="monster-card-container"
        size={size}
        onFlip={(isFlipped, cardId) => {
          // Optional: Track analytics or perform actions on flip
          if (isFlipped) {
            console.log(`Viewing details for monster ${cardId}`);
          }
        }}
      />
      
      {/* Card Art Viewer Modal */}
      <CardArtViewer
        isOpen={showArtViewer}
        onClose={() => setShowArtViewer(false)}
        artUrl={getCardArtUrl()}
        monsterName={monster.name}
        monsterSpecies={monster.species}
      />
    </>
  );
}

export default MonsterCard;