// RiddleBox.js - The riddle challenge: question, answer input, and verdict
// Appears once the monster has asked its riddle (choose_path completes)
// Handles: typing an answer, judging state, verdict display, and continuing on

import React, { useState } from 'react';
import { Card, CardSection, Button, Alert, Input, LoadingSpinner } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';

/**
 * RiddleBox component
 * The first bit of real gameplay: answer the monster's riddle
 */
function RiddleBox() {
  const { riddle, isJudgingAnswer, riddleResult, answerRiddle, continueExploring, exitText } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  const [answer, setAnswer] = useState('');

  if (exitText || !riddle) return null;

  const hasResult = !!riddleResult;

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

  const riddleTextStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-family-serif)',
    fontStyle: 'italic',
    whiteSpace: 'pre-wrap'
  };

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="lg" title="🧩 The monster speaks..." alignment="center" />

      {/* The riddle itself */}
      <CardSection type="content" alignment="center">
        <p style={riddleTextStyles}>"{riddle}"</p>
      </CardSection>

      {/* Answer input - until a verdict is in */}
      {!hasResult && (
        <CardSection type="content" alignment="center">
          <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <div style={{ minWidth: '280px' }}>
              <Input
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer..."
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
                  Judging...
                </>
              ) : (
                'Answer'
              )}
            </Button>
          </form>
        </CardSection>
      )}

      {/* Verdict */}
      {hasResult && (
        <CardSection type="content" alignment="center">
          <Alert
            type={riddleResult.correct ? 'success' : 'error'}
            title={riddleResult.correct ? '✅ Correct!' : '❌ Wrong!'}
          >
            {riddleResult.verdict}
          </Alert>

          <div style={{ marginTop: '20px' }}>
            <Button
              size="xl"
              icon="🧭"
              variant="primary"
              onClick={handleContinue}
            >
              Continue Exploring
            </Button>
          </div>
        </CardSection>
      )}
    </Card>
  );
}

export default RiddleBox;
