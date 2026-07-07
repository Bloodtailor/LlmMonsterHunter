// BattleLogBox.js - The click-through battle log
// The referee's narrations reveal one at a time; the backend runs ahead
// and the player reads at their own pace via "Next"

import React from 'react';
import { Card, CardSection, Button, LoadingSpinner, Badge } from '../../../shared/ui/index.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';

const IMPACT_LABELS = {
  none: null,
  light: { text: 'a solid hit', variant: 'warning' },
  heavy: { text: 'a heavy blow!', variant: 'error' },
  devastating: { text: 'DEVASTATING!', variant: 'error' },
  heal_light: { text: 'a soothing mend', variant: 'success' },
  heal_major: { text: 'a mighty restoration!', variant: 'success' },
};

function BattleLogBox() {
  const { isProcessing, currentNarration, pendingNarrations, turnResult, advanceLog } =
    useBattleContext();

  if (!isProcessing && !currentNarration) return null;

  const narrationStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-family-serif)',
    whiteSpace: 'pre-wrap',
  };

  // "Next" advances when there's more story, or applies the turn's
  // result once the backend is finished and everything has been read
  const hasMore = pendingNarrations.length > 0;
  const canFinish = !hasMore && !!turnResult;
  const waitingOnReferee = !hasMore && !turnResult;

  const impactBadge = currentNarration ? IMPACT_LABELS[currentNarration.impact] : null;
  const isTalk = currentNarration?.action === 'talk' && currentNarration?.dialogue;

  return (
    <Card size="xl" background="dark">
      <CardSection type="header" size="md" title="📜 Battle Log" alignment="center" />

      <CardSection type="content" alignment="center">
        {currentNarration ? (
          <>
            {currentNarration.autonomous && (
              <div style={{ marginBottom: '8px' }}>
                <Badge variant="warning" size="sm" pill>
                  🐾 {currentNarration.actor_name} acts on its own terms
                </Badge>
              </div>
            )}
            {isTalk && (
              <p
                style={{
                  ...narrationStyles,
                  fontStyle: 'italic',
                  color: 'var(--color-text-secondary)',
                }}
              >
                {currentNarration.actor_name}: "{currentNarration.dialogue}"
              </p>
            )}
            <p style={{ ...narrationStyles, ...(isTalk ? { fontStyle: 'italic' } : {}) }}>
              {isTalk ? `"${currentNarration.narration}"` : currentNarration.narration}
            </p>
            {impactBadge && (
              <div style={{ marginTop: '8px' }}>
                <Badge variant={impactBadge.variant} size="md">
                  {currentNarration.target_name}: {impactBadge.text}
                </Badge>
              </div>
            )}
          </>
        ) : (
          <div style={{ padding: '16px' }}>
            <LoadingSpinner size="section" type="spin" />
            <p style={{ marginTop: '12px', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
              The battle erupts...
            </p>
          </div>
        )}
      </CardSection>

      {currentNarration && (
        <CardSection type="content" alignment="center">
          <Button size="lg" variant="primary" onClick={advanceLog} disabled={waitingOnReferee}>
            {waitingOnReferee ? (
              <>
                <span style={{ marginRight: '8px' }}>
                  <LoadingSpinner size="sm" type="spin" />
                </span>
                The battle rages on...
              </>
            ) : canFinish ? (
              '▶ Continue'
            ) : (
              '▶ Next'
            )}
          </Button>
        </CardSection>
      )}
    </Card>
  );
}

export default BattleLogBox;
