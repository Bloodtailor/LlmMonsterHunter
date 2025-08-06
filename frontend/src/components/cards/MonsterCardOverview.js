// MonsterCardOverview.js - Overview side of monster card
// Quick visual summary: art, name, species, ability count
// "At-a-glance" information

import React from 'react';
import './monsterCard.css';
import { 
  IconButton, 
  CountBadge, 
  StatusBadge,
  Badge,
  EmptyState
} from '../../shared/ui/index.js';
import { CARD_SIZES } from '../../shared/constants/constants.js';
import { useParty } from '../../app/contexts/PartyContext/index.js';
import ToggleButton from '../../shared/ui/ToggleButton/ToggleButton.js';

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
    isFollowing,
    isPartyFull, 
    toggleParty, 
    isLoading: partyDisabled 
  } = useParty();

  const monsterIsInParty = isInParty(monster.id);
  const monsterIsFollowing = isFollowing(monster.id);


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
      case CARD_SIZES.SM:
        return "sm";
      case CARD_SIZES.MD:
        return "md";
      case CARD_SIZES.LG:
        return "md";
      case CARD_SIZES.XL:
        return "lg";
      default:
        return "sm";
    }
  };

  // Get button size based on card size
  const getButtonSize = () => {
    switch (size) {
      case CARD_SIZES.SM:
        return "sm";
      case CARD_SIZES.MD:
        return "md";
      case CARD_SIZES.LG:
        return "md";
      case CARD_SIZES.XL:
        return "lg";
      default:
        return "sm";
    }
  };

  // Helper to get ability count based on card size
  const getMaxAbilities = () => {
    switch (size) {
      case CARD_SIZES.SM: return 0;
      case CARD_SIZES.MD: return 2;
      case CARD_SIZES.LG: return 2;
      case CARD_SIZES.XL: return 3; 
      default: return 1;
    }
  };

  const maxAbilities = getMaxAbilities();

  return (
    <div className="monster-card-overview">
      {/* Party Toggle Button - Clean and simple with ToggleButton */}
      { showPartyToggle && monsterIsFollowing && (
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
      )}
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
            {onExpandCard != null && (
              <div className="monster-card-expand-button">
                <IconButton
                  icon="🔍"
                  variant="primary"
                  size={getButtonSize()}
                  onClick={handleExpandCard}
                  ariaLabel="View full-size monster card"
                />
              </div>
            )}
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
        {maxAbilities > 0 && (
          <div className="abilities-preview">
            <CountBadge
              count={monster.abilityCount}
              label="abilities"
              variant="secondary"
              icon="⚡"
              size={getBadgeSize()}
              className="abilities-count-badge"
            />
            
            {/* Show ability chips based on size */}
            {monster.abilities && monster.abilities.length > 0 && (
              <div className="ability-preview-chips">
                {/* NORMAL: 1 chip, LARGE: 2 chips, FULL: 3 chips */}
                {monster.abilities
                  .slice(0, maxAbilities)
                  .map((ability, index) => (
                    <Badge 
                      key={index} 
                      variant="primary" 
                      size={getBadgeSize()}
                      className="ability-preview-chip"
                    >
                      ⚡ {ability.name}
                    </Badge>
                  ))
                }
                
                {/* Show "more" indicator if there are additional abilities */}
                {monster.abilities.length > maxAbilities && (
                  <span className={`more-abilities-indicator more-abilities-indicator-${size}`}>
                    +{monster.abilities.length - maxAbilities} more
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