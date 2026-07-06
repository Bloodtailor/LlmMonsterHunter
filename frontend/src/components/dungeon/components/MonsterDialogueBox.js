// MonsterDialogueBox.js - The conversation with the encounter monster
// The monster greets the party and asks its question; the party answers
// in their own words. The LLM decides what every exchange leads to:
// keep talking, battle, allow passage, reward, punish, or join the party.

import React, { useState } from 'react';
import { Card, CardSection, Button, Textarea, LoadingSpinner } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

// How each resolved outcome is framed for the player
const OUTCOME_HEADERS = {
  begin_battle: '⚔️ The conversation turns hostile!',
  allow_passage: '🚶 The way is open',
  reward: '🎁 The monster grants a boon',
  punish: '⚡ The monster exacts a price',
  join_party: '🎉 A new companion!'
};

/**
 * MonsterDialogueBox component
 * The whole conversation lives here: history, reply input, and resolution
 */
function MonsterDialogueBox() {
  const {
    dialogue,
    isMonsterResponding,
    dialogueOutcome,
    respondToMonster,
    continueExploring,
    exitText
  } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  const [message, setMessage] = useState('');

  if (exitText || !dialogue || dialogue.length === 0) return null;

  const outcome = dialogueOutcome?.outcome || null;
  const joinedNames = dialogueOutcome?.joinedNames || [];

  // Send the party's words (form wrapper so Enter submits too)
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isMonsterResponding || outcome) return;
    respondToMonster(message.trim());
    setMessage('');
  };

  // Continue exploring: new paths from this location
  const handleContinue = () => {
    continueExploring();
    navigateToGameScreen('dungeon-doors');
  };

  // Everything the monster says shares one voice
  const monsterSpeechStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-family-serif)',
    fontStyle: 'italic',
    whiteSpace: 'pre-wrap',
    margin: 0
  };

  // The party's words look plainer - spoken, not performed
  const partySpeechStyles = {
    fontSize: 'var(--font-size-md)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-secondary)',
    whiteSpace: 'pre-wrap',
    margin: 0
  };

  const speakerLabelStyles = {
    fontSize: 'var(--font-size-sm)',
    fontWeight: 'bold',
    color: 'var(--color-text-muted)',
    marginBottom: '4px'
  };

  // A battle outcome hands the moment to the BattleIntroBox below
  const showContinueButton = outcome && outcome !== 'begin_battle';

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="lg" title="🗣️ The exchange" alignment="center" />

      {/* The conversation so far */}
      <CardSection type="content">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '720px', margin: '0 auto' }}>
          {dialogue.map((line, index) => {
            const isParty = line.speaker === 'The party';
            return (
              <div key={index} style={{ textAlign: isParty ? 'right' : 'left' }}>
                <div style={speakerLabelStyles}>{isParty ? '🛡️ The party' : `👹 ${line.speaker}`}</div>
                <p style={isParty ? partySpeechStyles : monsterSpeechStyles}>"{line.text}"</p>
              </div>
            );
          })}

          {isMonsterResponding && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
              <LoadingSpinner size="sm" type="spin" />
              The monster considers your words...
            </div>
          )}
        </div>
      </CardSection>

      {/* The party speaks - until the monster has decided */}
      {!outcome && (
        <CardSection type="content" alignment="center">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '640px', margin: '0 auto' }}>
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="What does your party say? Answer honestly, bargain, flatter, deceive... the monster will decide what to make of it."
              rows={3}
            />
            <div>
              <Button
                size="md"
                variant="primary"
                type="submit"
                disabled={!message.trim() || isMonsterResponding}
              >
                {isMonsterResponding ? 'Speaking...' : '💬 Speak'}
              </Button>
            </div>
          </form>
        </CardSection>
      )}

      {/* The monster has decided */}
      {outcome && (
        <>
          <CardSection type="header" size="md" title={OUTCOME_HEADERS[outcome] || 'The encounter resolves'} alignment="center" />

          {outcome === 'join_party' && joinedNames.length > 0 && (
            <CardSection type="content" alignment="center">
              <p style={{ color: 'var(--color-text-primary)', fontWeight: 'bold' }}>
                {joinedNames.join(', ')} now follows your party!
              </p>
            </CardSection>
          )}

          {showContinueButton && (
            <CardSection type="content" alignment="center">
              <Button
                size="xl"
                icon="🧭"
                variant="primary"
                onClick={handleContinue}
              >
                Continue Exploring
              </Button>
            </CardSection>
          )}
        </>
      )}
    </Card>
  );
}

export default MonsterDialogueBox;
