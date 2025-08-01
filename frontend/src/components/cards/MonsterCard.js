// MonsterCard Component - CLEAN ARCHITECTURE VERSION
// Uses clean monster domain object + UI primitives for maximum simplicity
// Focused purely on presentation - no state management or built-in modals
// Uses callback pattern for clean separation of concerns

import React from 'react';
import FlippableCard from '../../shared/ui/primitives/Card/FlippableCard.js'
import MonsterCardOverview from './MonsterCardOverview.js';
import MonsterCardDetails from './MonsterCardDetails.js';
import '../../styles/components/monsterCard.css';
import { CARD_SIZES } from '../../shared/constants/constants.js';

function MonsterCard({ 
  monster, 
  size = 'normal',
  
  // Party management (optional)
  showPartyToggle = false,
  isInParty = false,
  isPartyFull = false,
  onPartyToggle = null,
  partyDisabled = false,
  
  // Ability generation (optional)
  onAbilityGenerate = null,
  
  // Card viewer (callback pattern - no circular dependencies!)
  onExpandCard = null
}) {

  // Construct card art URL using clean monster object
  const getCardArtUrl = () => {
    if (!monster.cardArt.exists || !monster.cardArt.relativePath) return null;
    return `http://localhost:5000/api/monsters/card-art/${monster.cardArt.relativePath}`;
  };

  // Handle party toggle - just call parent callback
  const handlePartyToggle = (e) => {
    if (e && typeof e.stopPropagation === 'function') {
      e.stopPropagation();
    }
    if (onPartyToggle && !partyDisabled) {
      onPartyToggle(monster, isInParty);
    }
  };

  // Handle expand card - just call parent callback
  const handleExpandCard = (e) => {
    // Safely handle event if it exists and has stopPropagation
    if (e && typeof e.stopPropagation === 'function') {
      e.stopPropagation();
    }
    if (onExpandCard) {
      onExpandCard(monster);
    }
  };

  // Handle ability generation
  const handleAbilityGenerate = async (e) => {
    if (e && typeof e.stopPropagation === 'function') {
      e.stopPropagation();
    }
    if (onAbilityGenerate) {
      await onAbilityGenerate(monster.id);
    }
  };

  // Front of card - Use Overview component
  const frontContent = (
    <MonsterCardOverview
      monster={monster}
      size={size}
      showPartyToggle={true}
      isInParty={isInParty}
      isPartyFull={isPartyFull}
      onPartyToggle={handlePartyToggle}
      partyDisabled={partyDisabled}
      onExpandCard={handleExpandCard}
      getCardArtUrl={getCardArtUrl}
    />
  );

  // Back of card - Use Details component
  const backContent = (
    <MonsterCardDetails
      monster={monster}
      size={size}
      onAbilityGenerate={handleAbilityGenerate}
    />
  );

  return (
    <FlippableCard
      frontContent={frontContent}
      backContent={backContent}
      cardId={monster.id}
      className={`monster-card-container monster-card-${size}`}
      size={size}
      onFlip={(isFlipped) => {
        // Optional: Analytics or behavior tracking
        if (isFlipped) {
          console.log(`Viewing details for monster ${monster.id}`);
        }
      }}
    />
  );
}

export default MonsterCard;