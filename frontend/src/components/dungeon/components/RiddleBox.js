// RiddleBox.js - The monster's challenge: greeting, riddle, answer, and reaction
// Everything is the monster speaking to the party in character - it greets
// them with its own reason for the challenge, and it responds to their
// answer in its own voice (no plain right/wrong checkmark)

import React, { useState } from 'react';
import { Card, CardSection, Button, Input, LoadingSpinner } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * RiddleBox component
 * The first bit of real gameplay: answer the monster's riddle
 */
function RiddleBox() {
  const {
    encounterMonster,
    riddleGreeting,
    riddle,
    isJudgingAnswer,
    riddleResult,
    answerRiddle,
    continueExploring,
    exitText
  } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  const [answer, setAnswer] = useState('');

  if (exitText || !riddle) return null;

  const hasResult = !!riddleResult;
  const monsterName = encounterMonster?.name || 'The monster';

  // Submit the answer (form wrapper so Enter submits too)
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!answer.trim() || isJudgingAnswer || hasResult) return;
    answerRiddle(answer.trim());
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
    whiteSpace: 'pre-wrap'
  };

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="lg" title={`🗣️ ${monsterName} speaks...`} alignment="center" />

      {/* The monster's greeting - why it challenges the party */}
      {riddleGreeting && (
        <CardSection type="content" alignment="center">
          <p style={monsterSpeechStyles}>"{riddleGreeting}"</p>
        </CardSection>
      )}

      {/* The riddle itself */}
      <CardSection type="content" alignment="center">
        <p style={{ ...monsterSpeechStyles, fontWeight: 'bold' }}>"{riddle}"</p>
      </CardSection>

      {/* Answer input - until the monster has responded */}
      {!hasResult && (
        <CardSection type="content" alignment="center">
          <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <div style={{ minWidth: '280px' }}>
              <Input
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Speak your answer..."
              />
            </div>
            <Button
              size="md"
              variant="primary"
              type="submit"
              disabled={!answer.trim() || isJudgingAnswer}
            >
              {isJudgingAnswer ? (
                <>
                  <span style={{ marginRight: '8px' }}><LoadingSpinner size="sm" type="spin" /></span>
                  {monsterName} considers...
                </>
              ) : (
                'Answer'
              )}
            </Button>
          </form>
        </CardSection>
      )}

      {/* The monster responds to the party's answer, in its own voice */}
      {hasResult && (
        <>
          <CardSection type="content" alignment="center">
            <p style={monsterSpeechStyles}>"{riddleResult.response}"</p>
          </CardSection>

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
        </>
      )}
    </Card>
  );
}

export default RiddleBox;
