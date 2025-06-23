// Monster Card Component - USES FLIPPABLE CARD
// Front: Monster art + basic info, Back: Detailed stats and abilities
// Handles missing card art gracefully with placeholder

import React, { useState } from 'react';
import FlippableCard from '../ui/FlippableCard';

function MonsterCard({ monster, onAbilityGenerate = null }) {
  const [generatingAbility, setGeneratingAbility] = useState(false);

  // Handle card art - use placeholder if missing
  const getCardArtUrl = () => {
    if (monster.card_art?.exists && monster.card_art?.relative_path) {
      // In a real app, this would be served by the backend
      // For now, we'll use a placeholder since we can't serve the actual images
      return null; // Will use placeholder
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

  // Front of card - Art + Basic Info
  const frontContent = (
    <div className="monster-card-front">
      {/* Card Art */}
      <div className="monster-art-section">
        {getCardArtUrl() ? (
          <img 
            src={getCardArtUrl()} 
            alt={`${monster.name} card art`}
            className="monster-art"
          />
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
        
        <div className="monster-quick-stats">
          <div className="stat-chip">
            <span className="stat-label">HP</span>
            <span className="stat-value">{monster.stats.current_health}/{monster.stats.max_health}</span>
          </div>
          <div className="stat-chip">
            <span className="stat-label">ATK</span>
            <span className="stat-value">{monster.stats.attack}</span>
          </div>
          <div className="stat-chip">
            <span className="stat-label">DEF</span>
            <span className="stat-value">{monster.stats.defense}</span>
          </div>
          <div className="stat-chip">
            <span className="stat-label">SPD</span>
            <span className="stat-value">{monster.stats.speed}</span>
          </div>
        </div>

        {/* Ability Preview */}
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
    <FlippableCard
      frontContent={frontContent}
      backContent={backContent}
      cardId={monster.id}
      className="monster-card-container"
      size="normal"
      onFlip={(isFlipped, cardId) => {
        // Optional: Track analytics or perform actions on flip
        if (isFlipped) {
          console.log(`Viewing details for monster ${cardId}`);
        }
      }}
    />
  );
}

export default MonsterCard;