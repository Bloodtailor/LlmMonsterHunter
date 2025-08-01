// MonsterCardOverview.js - Overview side of monster card
// Quick visual summary: art, name, species, ability count
// "At-a-glance" information

import React from 'react';
import '../../styles/components/monsterCard.css';
import { 
  IconButton, 
  CountBadge, 
  StatusBadge,
  Badge,
  EmptyState
} from '../../shared/ui/index.js';
import { CARD_SIZES } from '../../shared/constants/constants.js';
import { useParty } from '../../app/contexts/PartyContext/index.js';
import ToggleButton from '../../shared/ui/ToggleButton/toggleButton.js';

function MonsterCardOverview({
  monster,
  size,
  
  // Party management
  showPartyToggle = false,
  
  // Card interactions
  onExpandCard = null,
  
  // URL helper
  getCardArtUrl
}) {

    // NEW: Get party data from context instead of props
  const { 
    isInParty, 
    isPartyFull, 
    toggleParty, 
    isLoading: partyDisabled 
  } = useParty();

  const monsterIsInParty = isInParty(monster.id);


  // Handle party toggle - just call parent callback
  const handlePartyToggle = (e) => {
    e.stopPropagation();
    if (showPartyToggle && !partyDisabled) {
      toggleParty(monster);
    }
  };

  // Handle expand card
  const handleExpandCard = (e) => {
    e.stopPropagation();
    if (onExpandCard) {
      onExpandCard(monster);
    }
  };

  // Get badge size based on card size
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

  // Get button size based on card size
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
    <div className="monster-card-overview">
      {/* Party Toggle Button - Clean and simple with ToggleButton */}
      <div className="monster-card-party-toggle">
        <ToggleButton
          isInCollection={monsterIsInParty}
          isCollectionFull={isPartyFull}
          isLoading={partyDisabled}
          onToggle={handlePartyToggle}
          itemName={monster.name}
          collectionName="party"
          size={getButtonSize()}
          maxItems={4}
        />
      </div>
      {/* Main Art Section - Full Card Coverage */}
      <div className="monster-art-section">
        {getCardArtUrl() ? (
          <>
            <img 
              src={getCardArtUrl()} 
              alt={`${monster.name} card art`}
              className="monster-art-image"
            />
            {/* Expand Button Overlay */}
            <div className="monster-card-expand-button">
              <IconButton
                icon="🔍"
                variant="secondary"
                size={getButtonSize()}
                onClick={handleExpandCard}
                ariaLabel="View full-size monster card"
              />
            </div>
          </>
        ) : (
          <div className="monster-art-placeholder">
            <EmptyState
              icon="🐲"
              title="No Card Art"
              message="Generate card art for this monster"
              size="sm"
            />
          </div>
        )}
      </div>

      {/* Info Overlay - Positioned over image */}
      <div className="monster-info-overlay">
        <div className="monster-header">
          <h3 className={`monster-name monster-name-${size}`}>{monster.name}</h3>
          <Badge variant="info" size={getBadgeSize()} className="monster-species-badge">
            {monster.species}
          </Badge>
        </div>

        {/* Ability Preview - Adapt content based on size */}
        {size !== CARD_SIZES.SMALL && (
          <div className="abilities-preview">
            <CountBadge
              count={monster.abilityCount}
              label="abilities"
              icon="⚡"
              size={getBadgeSize()}
              className="abilities-count-badge"
            />
            
            {/* Show ability chips based on size */}
            {monster.abilities && monster.abilities.length > 0 && (
              <div className="ability-preview-chips">
                {/* NORMAL: 1 chip, LARGE: 2 chips, FULL: 3 chips */}
                {monster.abilities
                  .slice(0, 
                    size === CARD_SIZES.NORMAL ? 1 : 
                    size === CARD_SIZES.LARGE ? 2 : 
                    size === CARD_SIZES.FULL ? 3 : 0
                  )
                  .map((ability, index) => (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      size={getBadgeSize()}
                      className="ability-preview-chip"
                    >
                      ⚡ {ability.name}
                    </Badge>
                  ))
                }
                
                {/* Show "more" indicator if there are additional abilities */}
                {monster.abilities.length > (
                  size === CARD_SIZES.NORMAL ? 1 : 
                  size === CARD_SIZES.LARGE ? 2 : 
                  size === CARD_SIZES.FULL ? 3 : 0
                ) && (
                  <span className={`more-abilities-indicator more-abilities-indicator-${size}`}>
                    +{monster.abilities.length - (
                      size === CARD_SIZES.NORMAL ? 1 : 
                      size === CARD_SIZES.LARGE ? 2 : 
                      size === CARD_SIZES.FULL ? 3 : 0
                    )} more
                  </span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MonsterCardOverview;