// ExplorePanel.js - The party looks around and decides what to do
// The most common arrival: no scripted challenge, just the place itself.
// Monsters in the area? Talk, strike first, or sneak past. Empty area?
// Set up camp (the monsters rest and chat) or press onward.

import React, { useState } from 'react';
import { Card, CardSection, Button, Textarea, LoadingSpinner } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';

/**
 * ExplorePanel component
 * Action hub for the location_explore event - hides itself once a
 * conversation starts (MonsterDialogueBox) or a battle begins (BattleIntroBox)
 */
function ExplorePanel() {
  const {
    monstersPresent,
    dialogue,
    sneakResult,
    isSneaking,
    isAmbushing,
    isMonsterResponding,
    campText,
    isCamping,
    hasCamped,
    respondToMonster,
    sneakPast,
    surpriseAttack,
    setupCamp,
    continueExploring,
    exitText,
  } = useDungeon();
  const { displayedBattle } = useBattleContext();
  const { navigateToGameScreen } = useNavigation();

  const [isTalking, setIsTalking] = useState(false);
  const [message, setMessage] = useState('');

  // Only for explore events, and only until another system takes over
  if (exitText || monstersPresent === null) return null;
  if (dialogue && dialogue.length > 0) return null; // conversation started
  if (displayedBattle?.in_battle) return null; // battle started

  const isActing = isSneaking || isAmbushing || isMonsterResponding;

  // Continue exploring: new paths from this location
  const handleContinue = () => {
    continueExploring();
    navigateToGameScreen('dungeon-doors');
  };

  // Open talks - the party speaks first; the conversation takes over from there
  const handleTalkSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isActing) return;
    respondToMonster(message.trim());
    setMessage('');
  };

  const narrationStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-family-serif)',
    fontStyle: 'italic',
    whiteSpace: 'pre-wrap',
  };

  // === MONSTERS IN THE AREA ===
  if (monstersPresent) {
    // The sneak has been judged - success shows here (failure becomes a battle)
    if (sneakResult) {
      if (!sneakResult.success) return null; // BattleIntroBox owns the moment
      return (
        <Card size="xl" background="light">
          <CardSection
            type="header"
            size="lg"
            title="🤫 Slipped past unnoticed"
            alignment="center"
          />
          <CardSection type="content" alignment="center">
            <p style={narrationStyles}>{sneakResult.narration}</p>
          </CardSection>
          <CardSection type="content" alignment="center">
            <Button size="xl" icon="🧭" variant="primary" onClick={handleContinue}>
              Continue Exploring
            </Button>
          </CardSection>
        </Card>
      );
    }

    return (
      <Card size="xl" background="light">
        <CardSection
          type="header"
          size="lg"
          title="👀 They haven't noticed you yet..."
          alignment="center"
        />

        <CardSection type="content" alignment="center">
          <p style={{ color: 'var(--color-text-secondary)' }}>
            The creatures are unaware of your presence. What does the party do?
          </p>
        </CardSection>

        {/* Approach and talk */}
        {isTalking ? (
          <CardSection type="content" alignment="center">
            <form
              onSubmit={handleTalkSubmit}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                maxWidth: '640px',
                margin: '0 auto',
              }}
            >
              <Textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="The party steps into view. What do they say? A greeting, a question, an offer..."
                rows={3}
              />
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <Button
                  size="md"
                  variant="primary"
                  type="submit"
                  disabled={!message.trim() || isActing}
                >
                  {isMonsterResponding ? 'Approaching...' : '💬 Approach & Speak'}
                </Button>
                <Button
                  size="md"
                  variant="secondary"
                  onClick={() => setIsTalking(false)}
                  disabled={isActing}
                >
                  Back
                </Button>
              </div>
            </form>
          </CardSection>
        ) : (
          <CardSection type="content" alignment="center">
            <div
              style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}
            >
              <Button
                size="lg"
                icon="💬"
                variant="primary"
                onClick={() => setIsTalking(true)}
                disabled={isActing}
              >
                Talk to Them
              </Button>
              <Button
                size="lg"
                icon="⚔️"
                variant="danger"
                onClick={surpriseAttack}
                disabled={isActing}
              >
                {isAmbushing ? 'Striking...' : 'Surprise Attack'}
              </Button>
              <Button
                size="lg"
                icon="🤫"
                variant="secondary"
                onClick={sneakPast}
                disabled={isActing}
              >
                {isSneaking ? 'Sneaking...' : 'Sneak Past'}
              </Button>
            </div>
            {isActing && (
              <div style={{ marginTop: '16px' }}>
                <LoadingSpinner size="sm" type="spin" />
              </div>
            )}
          </CardSection>
        )}
      </Card>
    );
  }

  // === THE AREA IS CLEAR ===
  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="lg" title="🏞️ The area is clear" alignment="center" />

      {/* The camp scene streams in once camp is set */}
      {campText && (
        <CardSection type="content">
          <p style={{ ...narrationStyles, maxWidth: '720px', margin: '0 auto' }}>{campText}</p>
        </CardSection>
      )}

      <CardSection type="content" alignment="center">
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {!hasCamped && !isCamping && (
            <Button size="lg" icon="🏕️" variant="secondary" onClick={setupCamp}>
              Set Up Camp
            </Button>
          )}
          {isCamping && (
            <Button size="lg" icon="🏕️" variant="secondary" disabled>
              Settling in...
            </Button>
          )}
          <Button size="lg" icon="🧭" variant="primary" onClick={handleContinue}>
            Continue Exploring
          </Button>
        </div>
      </CardSection>
    </Card>
  );
}

export default ExplorePanel;
