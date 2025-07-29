// MonsterCardDetails.js - Details side of monster card
// Full information view: stats, description, backstory, personality traits
// "Everything about this monster"

import React from 'react';
import '../../styles/components/monsterCard.css';
import { 
  Card,
  CardSection,
  IconButton, 
  StatusBadge,
  Badge,
  EmptyState
} from '../../shared/ui/index.js';
import { CARD_SIZES } from '../../shared/constants.js';

function MonsterCardDetails({
  monster,
  size = 'normal', // Add size prop
  
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
      case CARD_SIZES.SMALL:
        return "sm";
      case CARD_SIZES.NORMAL:
        return "sm";
      case CARD_SIZES.LARGE:
        return "md";
      case CARD_SIZES.FULL:
        return "lg";
      default:
        return "sm";
    }
  };

  // Determine button size based on card size  
  const getButtonSize = () => {
    switch (size) {
      case CARD_SIZES.SMALL:
        return "sm";
      case CARD_SIZES.NORMAL:
        return "sm";
      case CARD_SIZES.LARGE:
        return "md";
      case CARD_SIZES.FULL:
        return "md";
      default:
        return "sm";
    }
  };

  return (
    <Card variant="flat" padding="md" className={`monster-card-details monster-card-details-${size}`}>
      
      {/* Header */}
      <CardSection type="header" title={monster.name}>
        <Badge variant="info" size={getBadgeSize()}>
          {monster.species}
        </Badge>
      </CardSection>

      {/* Description - Always show */}
      <CardSection type="content">
        <p className={`monster-card-description monster-card-description-${size}`}>
          {monster.description}
        </p>
      </CardSection>

      {/* Backstory - Hide on small size */}
      {size !== CARD_SIZES.SMALL && monster.backstory && (
        <CardSection type="content" title="📖 Backstory">
          <p className={`monster-card-backstory monster-card-backstory-${size}`}>
            {monster.backstory}
          </p>
        </CardSection>
      )}

      {/* Stats */}
      <CardSection type="content" title="Stats" alignment='left'>
        <div className="monster-card-stats-grid">
          <div className="monster-card-stat-row">
            <span>Health:</span>
            <span>{monster.stats.currentHealth}/{monster.stats.maxHealth}</span>
          </div>
          <div className="monster-card-stat-row">
            <span>Attack:</span>
            <Badge variant="primary" size={getBadgeSize()}>{monster.stats.attack}</Badge>
          </div>
          <div className="monster-card-stat-row">
            <span>Defense:</span>
            <Badge variant="primary" size={getBadgeSize()}>{monster.stats.defense}</Badge>
          </div>
          <div className="monster-card-stat-row">
            <span>Speed:</span>
            <Badge variant="primary" size={getBadgeSize()}>{monster.stats.speed}</Badge>
          </div>
        </div>
      </CardSection>

      {/* Abilities - Show different amounts based on size */}
      <CardSection 
        type="content" 
        title="Abilities"
        action={onAbilityGenerate && (
          <IconButton
            icon="✨"
            variant="secondary" 
            size={getButtonSize()}
            onClick={handleAbilityGenerate}
            ariaLabel="Generate new ability"
          />
        )}
      >
        {monster.abilities && monster.abilities.length > 0 ? (
          <div className="monster-card-abilities-list">
            {/* Show different number of abilities based on size */}
            {monster.abilities
              .slice(0, 
                size === CARD_SIZES.SMALL ? 2 :
                size === CARD_SIZES.NORMAL ? 3 :
                size === CARD_SIZES.LARGE ? 4 :
                size === CARD_SIZES.FULL ? undefined : 3 // FULL shows all
              )
              .map((ability, index) => (
                <div key={index} className={`monster-card-ability-item monster-card-ability-item-${size}`}>
                  <div className={`monster-card-ability-name monster-card-ability-name-${size}`}>⚡ {ability.name}</div>
                  <div className={`monster-card-ability-description monster-card-ability-description-${size}`}>{ability.description}</div>
                </div>
              ))
            }
            
            {/* Show "more abilities" indicator if there are more */}
            {size !== CARD_SIZES.FULL && monster.abilities.length > (
              size === CARD_SIZES.SMALL ? 2 :
              size === CARD_SIZES.NORMAL ? 3 :
              size === CARD_SIZES.LARGE ? 4 : 3
            ) && (
              <div className={`more-abilities-indicator more-abilities-indicator-${size}`}>
                +{monster.abilities.length - (
                  size === CARD_SIZES.SMALL ? 2 :
                  size === CARD_SIZES.NORMAL ? 3 :
                  size === CARD_SIZES.LARGE ? 4 : 3
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

      {/* Personality Traits - Hide on small, show limited on normal/large, show all on full */}
      {size !== CARD_SIZES.SMALL && monster.personalityTraits && monster.personalityTraits.length > 0 && (
        <CardSection type="footer" title="Personality">
          <div className="monster-card-traits-list">
            {monster.personalityTraits
              .slice(0, 
                size === CARD_SIZES.NORMAL ? 3 :
                size === CARD_SIZES.LARGE ? 5 :
                size === CARD_SIZES.FULL ? undefined : 3 // FULL shows all
              )
              .map((trait, index) => (
                <Badge key={index} variant="secondary" size={getBadgeSize()}>
                  {trait}
                </Badge>
              ))
            }
            
            {/* Show "more traits" indicator if there are more */}
            {size !== CARD_SIZES.FULL && monster.personalityTraits.length > (
              size === CARD_SIZES.NORMAL ? 3 :
              size === CARD_SIZES.LARGE ? 5 : 3
            ) && (
              <span className={`more-traits-indicator more-traits-indicator-${size}`}>
                +{monster.personalityTraits.length - (
                  size === CARD_SIZES.NORMAL ? 3 :
                  size === CARD_SIZES.LARGE ? 5 : 3
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