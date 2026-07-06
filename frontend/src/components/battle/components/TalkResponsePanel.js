// TalkResponsePanel.js - An enemy is talking to you mid-battle
// The player types their reply; the LLM adjudicates what comes of it
// (fight on, they yield, they flee, they join, or mercy is granted)

import React, { useState } from 'react';
import { Card, CardSection, Button, Textarea } from '../../../shared/ui/index.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';

function TalkResponsePanel() {
  const { pendingTalk, isProcessing, outcome, respondToTalk } = useBattleContext();
  const [reply, setReply] = useState('');

  if (!pendingTalk || isProcessing || outcome) return null;

  const speechStyles = {
    fontSize: 'var(--font-size-lg)',
    lineHeight: 'var(--line-height-relaxed)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-family-serif)',
    fontStyle: 'italic',
    whiteSpace: 'pre-wrap'
  };

  const handleRespond = () => {
    if (!reply.trim()) return;
    respondToTalk(reply.trim());
    setReply('');
  };

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="md" title={`💬 ${pendingTalk.speakerName} speaks to you...`} alignment="center" />

      <CardSection type="content" alignment="center">
        <p style={speechStyles}>"{pendingTalk.dialogue}"</p>
      </CardSection>

      <CardSection type="content">
        <div style={{ maxWidth: '640px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Textarea
            value={reply}
            onChange={(e) => setReply(e.target.value)}
            placeholder="What does your party say back?"
            rows={3}
          />
          <div style={{ textAlign: 'center' }}>
            <Button
              size="lg"
              icon="💬"
              variant="primary"
              disabled={!reply.trim()}
              onClick={handleRespond}
            >
              Respond
            </Button>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default TalkResponsePanel;
