// MonsterCard Component - REFACTORED WITH CLEAN ARCHITECTURE
// Uses clean monster domain object + UI primitives for maximum simplicity
// Focused purely on presentation - no state management or data transformation

import React, { useState } from 'react';
import FlippableCard from './FlippableCard.js';
import MonsterCardOverview from './MonsterCardOverview.js';
import MonsterCardDetails from './MonsterCardDetails.js';
import '../../styles/components/monsterCard.css';
import { 
  Card,
  CardSection,
  IconButton, 
  CountBadge, 
  StatusBadge, 
  EmptyState,
  EMPTY_STATE_PRESETS
} from '../../shared/ui/index.js';
import { CARD_SIZES } from '../../shared/constants.js';

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
  
  // Card viewer (optional)
  onExpandCard = null
}) {
  const [showCardViewer, setShowCardViewer] = useState(false);

  // Construct card art URL using clean monster object
  const getCardArtUrl = () => {
    if (!monster.cardArt.exists || !monster.cardArt.relativePath) return null;
    return `http://localhost:5000/api/monsters/card-art/${monster.cardArt.relativePath}`;
  };

  // Handle party toggle - just call parent callback
  const handlePartyToggle = (e) => {
    e.stopPropagation();
    if (onPartyToggle && !partyDisabled) {
      onPartyToggle(monster, isInParty);
    }
  };

  // Handle expand card
  const handleExpandCard = (e) => {
    e.stopPropagation();
    if (onExpandCard) {
      onExpandCard(monster);
    } else {
      setShowCardViewer(true);
    }
  };

  // Handle ability generation
  const handleAbilityGenerate = async (e) => {
    e.stopPropagation();
    if (onAbilityGenerate) {
      await onAbilityGenerate(monster.id);
    }
  };

  // Front of card - Use Overview component
  const frontContent = (
    <MonsterCardOverview
      monster={monster}
      size={size}
      showPartyToggle={showPartyToggle}
      isInParty={isInParty}
      isPartyFull={isPartyFull}
      onPartyToggle={onPartyToggle}
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
    <>
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
      
      {/* Simple Card Viewer Modal */}
      {showCardViewer && (
        <div 
          className="monster-card-modal-overlay"
          onClick={() => setShowCardViewer(false)}
        >
          <Card
            variant="elevated"
            padding="lg"
            className="monster-card-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <CardSection type="header" title={`${monster.name} - Full View`}>
              <IconButton
                icon="✕"
                variant="secondary"
                onClick={() => setShowCardViewer(false)}
                ariaLabel="Close monster card viewer"
              />
            </CardSection>
            
            <CardSection type="content">
              <FlippableCard
                frontContent={
                  <MonsterCardOverview
                    monster={monster}
                    size={CARD_SIZES.FULL}
                    showPartyToggle={showPartyToggle}
                    isInParty={isInParty}
                    isPartyFull={isPartyFull}
                    onPartyToggle={onPartyToggle}
                    partyDisabled={partyDisabled}
                    onExpandCard={handleExpandCard}
                    getCardArtUrl={getCardArtUrl}
                  />
                }
                backContent={
                  <MonsterCardDetails
                    monster={monster}
                    size={CARD_SIZES.FULL}
                    onAbilityGenerate={handleAbilityGenerate}
                  />
                }
                size={CARD_SIZES.FULL}
              />
            </CardSection>
          </Card>
        </div>
      )}
    </>
  );
}

export default MonsterCard;