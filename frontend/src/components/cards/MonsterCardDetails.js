// MonsterCardDetails.js - Details side of monster card
// Full information view: stats, description, backstory, personality traits
// Uses CardSection automatic typography scaling - NO manual size classes!

import React from 'react';
import './monsterCard.css';
import { 
  Card,
  CardSection,
  IconButton, 
  StatusBadge,
  Badge,
  EmptyState
} from '../../shared/ui/index.js';
import { CARD_SIZES } from '../../shared/constants/constants.js';

function MonsterCardDetails({
  monster,
  size = 'md',
  
  // Ability generation
  onAbilityGenerate = null
}) {

  // Handle ability generation
  const handleAbilityGenerate = async (e) => {
    e.stopPropagation();
    if (onAbilityGenerate) {
      await onAbilityGenerate(monster.id);
    }
  };

  // Determine badge size based on card size
  const getBadgeSize = () => {
    switch (size) {
      case CARD_SIZES.SM: return "sm";
      case CARD_SIZES.MD: return "md";
      case CARD_SIZES.LG: return "md";
      case CARD_SIZES.XL: return "lg";
      default: return "sm";
    }
  };

  // Determine button size based on card size  
  const getButtonSize = () => {
    switch (size) {
      case CARD_SIZES.SM: return "sm";
      case CARD_SIZES.MD: return "sm";
      case CARD_SIZES.LG: return "md";
      case CARD_SIZES.XL: return "md";
      default: return "sm";
    }
  };

  return (
    <Card variant="flat" padding="md" className="monster-card-details">
      
      {/* Header - CardSection handles title typography automatically */}
      <CardSection type="header" title={monster.name} size={size}>
        <Badge variant="info" size={getBadgeSize()}>
          {monster.species}
        </Badge>
      </CardSection>

      {/* Description - CardSection handles paragraph typography automatically */}
      <CardSection type="content" size={size}>
        <p>{monster.description}</p>
      </CardSection>

      {/* Backstory - Hide on small size, CardSection handles typography */}
      {size !== CARD_SIZES.SM && monster.backstory && (
        <CardSection type="content" title="📖 Backstory" size={size}>
          <p>{monster.backstory}</p>
        </CardSection>
      )}

      {/* Stats - CardSection handles typography automatically */}
      <CardSection type="content" title="Stats" alignment='left' size={size}>
        <div className="monster-card-stats-grid">
          <div className="stat-item">
            <span>Health: {monster.health}</span>
            <span className="stat-value"></span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Attack:</span>
            <span className="stat-value">{monster.attack}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Defense:</span>
            <span className="stat-value">{monster.defense}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Speed:</span>
            <span className="stat-value">{monster.speed}</span>
          </div>
        </div>
      </CardSection>

      {/* Abilities - CardSection handles typography automatically */}
      <CardSection type="content" title="Abilities" alignment='left' size={size}>
        {monster.abilities && monster.abilities.length > 0 ? (
          <div className="monster-card-abilities-list">
            {/* Show limited abilities based on card size */}
            {monster.abilities
              .slice(0, 
                size === CARD_SIZES.SM ? 2 :
                size === CARD_SIZES.MD ? 3 :
                size === CARD_SIZES.LG ? 4 : 3
              )
              .map((ability, index) => (
                <div key={index} className="monster-card-ability-item">
                  <div className="monster-card-ability-name">
                    {ability.name}
                  </div>
                  <div className="monster-card-ability-description">
                    {ability.description}
                  </div>
                </div>
              ))
            }
            
            {/* Show "more abilities" indicator if there are more */}
            {size !== CARD_SIZES.XL && monster.abilities.length > (
              size === CARD_SIZES.SM ? 2 :
              size === CARD_SIZES.MD ? 3 :
              size === CARD_SIZES.LG ? 4 : 3
            ) && (
              <div className={`more-abilities-indicator more-abilities-indicator-${size}`}>
                +{monster.abilities.length - (
                  size === CARD_SIZES.SM ? 2 :
                  size === CARD_SIZES.MD ? 3 :
                  size === CARD_SIZES.LG ? 4 : 3
                )} more abilities
              </div>
            )}
          </div>
        ) : (
          <EmptyState
            icon="⚡"
            title="No Abilities Yet"
            message="Generate some abilities!"
            size="sm"
          />
        )}
      </CardSection>

      {/* Personality Traits - Hide on small, CardSection handles typography */}
      {size !== CARD_SIZES.SM && monster.personalityTraits && monster.personalityTraits.length > 0 && (
        <CardSection type="footer" title="Personality" size={size}>
          <div className="monster-card-traits-list">
            {monster.personalityTraits
              .slice(0, 
                size === CARD_SIZES.MD ? 3 :
                size === CARD_SIZES.LG ? 5 :
                size === CARD_SIZES.XL ? undefined : 3 // XL shows all
              )
              .map((trait, index) => (
                <Badge key={index} variant="secondary" size={getBadgeSize()}>
                  {trait}
                </Badge>
              ))
            }
            
            {/* Show "more traits" indicator if there are more */}
            {size !== CARD_SIZES.XL && monster.personalityTraits.length > (
              size === CARD_SIZES.MD ? 3 :
              size === CARD_SIZES.LG ? 5 : 3
            ) && (
              <span className={`more-traits-indicator more-traits-indicator-${size}`}>
                +{monster.personalityTraits.length - (
                  size === CARD_SIZES.MD ? 3 :
                  size === CARD_SIZES.LG ? 5 : 3
                )} more
              </span>
            )}
          </div>
        </CardSection>
      )}
      
    </Card>
  );
}

export default MonsterCardDetails;