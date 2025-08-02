// MonsterCardDetails.js - Details side of monster card
// Full information view: stats, description, backstory, personality traits
// Uses new CardSection system and useTypographyScale hook for consistent typography

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
import { useTypographyScale } from '../../shared/hooks/useTypographyScale.js';

function MonsterCardDetails({
  monster,
  size = 'md',
  
  // Ability generation
  onAbilityGenerate = null
}) {


  const classType = 'monster';
  
  // Get typography scaling functions
  const { getTextSize } = useTypographyScale(size, classType);

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

  // Helper to get ability count based on card size
  const getMaxAbilities = () => {
    switch (size) {
      case CARD_SIZES.SM: return 2;
      case CARD_SIZES.MD: return 3;
      case CARD_SIZES.LG: return 4;
      case CARD_SIZES.XL: return undefined; // Show all
      default: return 3;
    }
  };

  // Helper to get trait count based on card size
  const getMaxTraits = () => {
    switch (size) {
      case CARD_SIZES.SM: return 0; // Hide on small
      case CARD_SIZES.MD: return 3;
      case CARD_SIZES.LG: return 5;
      case CARD_SIZES.XL: return 99; // Show all
      default: return 3;
    }
  };

  const maxAbilities = getMaxAbilities();
  const maxTraits = getMaxTraits();

  return (
    <Card variant="flat" padding="md" className="monster-card-details">
      
      {/* Header - CardSection automatically handles title typography */}
      <CardSection 
        type="header" 
        size={size} 
        classType={classType}
        title={monster.name}
        alignment='center'
      >
        <Badge variant="info" size={getBadgeSize()}>
          {monster.species}
        </Badge>
      </CardSection>

      {/* Description - CardSection handles content typography */}
      <CardSection type="content" size={size} classType={classType}>
        <p className={getTextSize('body')}>{monster.description}</p>
      </CardSection>

      {/* Backstory - Hide on small size */}
      {size !== CARD_SIZES.SM && monster.backstory && (
        <CardSection 
          type="content" 
          size={size} 
          classType={classType}
          title="📖 Backstory"
        >
          <p className={getTextSize('body')}>{monster.backstory}</p>
        </CardSection>
      )}

      {/* Stats */}
      <CardSection 
        type="content" 
        size={size} 
        classType={classType}
        title="Stats"
      >
        <div className="monster-card-stats-grid">
          <div className="stat-item">
            <span className={getTextSize('caption')}>Health:</span>
            <span className={`stat-value ${getTextSize('caption')}`}>
              {monster.stats?.currentHealth || 0}/{monster.stats?.maxHealth || 0}
            </span>
          </div>
          <div className="stat-item">
            <span className={getTextSize('caption')}>Attack:</span>
            <span className={`stat-value ${getTextSize('caption')}`}>
              {monster.stats?.attack || 0}
            </span>
          </div>
          <div className="stat-item">
            <span className={getTextSize('caption')}>Defense:</span>
            <span className={`stat-value ${getTextSize('caption')}`}>
              {monster.stats?.defense || 0}
            </span>
          </div>
          <div className="stat-item">
            <span className={getTextSize('caption')}>Speed:</span>
            <span className={`stat-value ${getTextSize('caption')}`}>
              {monster.stats?.speed || 0}
            </span>
          </div>
        </div>
      </CardSection>

      {/* Abilities */}
      <CardSection 
        type="content" 
        size={size} 
        classType={classType}
        title="Abilities"
        action={onAbilityGenerate && (
          <IconButton
            icon="⚡"
            variant="ghost"
            size={getButtonSize()}
            onClick={handleAbilityGenerate}
            ariaLabel="Generate new ability"
          />
        )}
      >
        {monster.abilities && monster.abilities.length > 0 ? (
          <div className="monster-card-abilities-list">
            {/* Show limited abilities based on card size */}
            {monster.abilities
              .slice(0, maxAbilities)
              .map((ability, index) => (
                <div key={index} className="monster-card-ability-item">
                  <div className={`monster-card-ability-name ${getTextSize('subtitle')}`}>
                    {ability.name}
                  </div>
                  <div className={`monster-card-ability-description ${getTextSize('caption')}`}>
                    {ability.description}
                  </div>
                </div>
              ))
            }
            
            {/* Show "more abilities" indicator if there are more */}
            {maxAbilities && monster.abilities.length > maxAbilities && (
              <div className={`more-abilities-indicator ${getTextSize('caption')}`}>
                +{monster.abilities.length - maxAbilities} more abilities
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

      {/* Personality Traits - Hide on small size */}
      {maxTraits > 0 && monster.personalityTraits && monster.personalityTraits.length > 0 && (
        <CardSection 
          type="content" 
          size={size} 
          classType={classType}
          title="Personality"
        >
          <div className="monster-card-traits-list">
            {monster.personalityTraits
              .slice(0, maxTraits)
              .map((trait, index) => (
                <Badge key={index} variant="secondary" size={getBadgeSize()}>
                  {trait}
                </Badge>
              ))
            }
            
            {/* Show "more traits" indicator if there are more */}
            {maxTraits && monster.personalityTraits.length > maxTraits && (
              <span className={`more-traits-indicator ${getTextSize('caption')}`}>
                +{monster.personalityTraits.length - maxTraits} more
              </span>
            )}
          </div>
        </CardSection>
      )}

      <CardSection type="footer" size={size} classType={classType}></CardSection>
      
    </Card>
  );
}

export default MonsterCardDetails;