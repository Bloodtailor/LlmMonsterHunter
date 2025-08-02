// MonsterCard Component - CLEAN ARCHITECTURE VERSION
// Uses clean monster domain object + UI primitives for maximum simplicity
// Focused purely on presentation - no state management or built-in modals
// Uses callback pattern for clean separation of concerns

import React from 'react';
import FlippableCard from '../../shared/ui/Card/FlippableCard.js'
import MonsterCardOverview from './MonsterCardOverview.js';
import MonsterCardDetails from './MonsterCardDetails.js';
import './monsterCard.css';
import { CARD_SIZES } from '../../shared/constants/constants.js';

function MonsterCard({ 
  monster, 
  size = 'md', // Updated to use new CARD_SIZES
  
  // Party management (optional)
  showPartyToggle = false,
  
  // Card viewer (callback pattern - no circular dependencies!)
  onExpandCard = null
}) {

  // Construct card art URL using clean monster object
  const getCardArtUrl = () => {
    if (!monster.cardArt.exists || !monster.cardArt.relativePath) return null;
    return `http://localhost:5000/api/monsters/card-art/${monster.cardArt.relativePath}`;
  };

  // Handle expand card - just call parent callback
  const handleExpandCard = onExpandCard
  ? (e) => {
      if (e && typeof e.stopPropagation === 'function') {
        e.stopPropagation();
      }
      onExpandCard(monster);
    }
  : null;


  // Front of card - Use Overview component
  const frontContent = (
    <MonsterCardOverview
      monster={monster}
      size={size}
      showPartyToggle={showPartyToggle}
      onExpandCard={handleExpandCard}
      getCardArtUrl={getCardArtUrl}
    />
  );

  // Back of card - Use Details component
  const backContent = (
    <MonsterCardDetails
      monster={monster}
      size={size}
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