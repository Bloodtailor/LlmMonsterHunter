// PartyDisplay Component - Shows current party members with optional empty slots
// Uses PartyContext to get party data and individual monster objects
// Displays in same flex layout style as MonsterSanctuaryScreen

import React from 'react';
import { useParty } from '../../app/contexts/PartyContext/index.js';
import { useMonsterCardViewer } from '../cards/useMonsterCardViewer.js';
import { GAME_RULES } from '../../shared/constants/constants.js';
import { 
  Select,
  Alert,
  EmptyState,
  EMPTY_STATE_PRESETS,
  Card,
  CardSection,
  EmptyPartySlot,
  LoadingSpinner
} from "../../shared/ui/index.js";

function PartyDisplay({
  cardSize = 'sm',
  showTitle = true,
  maxWidth = null,
  showEmptySlots = true,
  showPartyToggle = true,
  className = '',
  style = {}
}) {
  
  // Get party data from context
  const { partySize, partyMonsters, isLoading } = useParty();
  
  // Get card viewer functionality
  const { MonsterCard, viewer } = useMonsterCardViewer();
  
  // Create empty slot placeholders
  const emptySlots = showEmptySlots 
    ? Array(GAME_RULES.MAX_PARTY_SIZE - partySize).fill(null)
    : [];

  const title = showTitle && `🛡️ Active Party (${partySize}/${GAME_RULES.MAX_PARTY_SIZE})`
  
  return (
    <Card >
      <CardSection title={title} type='header'></CardSection>

      <div style={{ height: `var(--card-height-${cardSize})` }}>
        { isLoading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <LoadingSpinner size="section" type="spin" />
          </div>

        ) : (
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-evenly'
          }}>
            {/* Render party monster cards */}
            {(partyMonsters || []).map(monster => (
              <MonsterCard
                key={monster.id}
                monster={monster}
                size={cardSize}
                showPartyToggle={showPartyToggle}
                hideFlipHint={true}
              />
            ))}
            
            {/* Render empty slot placeholders */}
            {emptySlots.map((_, index) => (
              <EmptyPartySlot size={cardSize}></EmptyPartySlot>
            ))}
          </div>
        )}
      </div>

      {viewer}
    </Card>
  );
}

export default PartyDisplay;