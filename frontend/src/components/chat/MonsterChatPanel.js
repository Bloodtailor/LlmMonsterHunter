// MonsterChatPanel.js - The conversation with one following monster
// The persistent thread (older pages load on demand), the streaming
// reply, the input form, and the "will remember this" moments.
// Speech styling mirrors MonsterDialogueBox: the monster performs,
// the adventurer just talks.

import React, { useEffect, useRef, useState } from 'react';
import {
  Card,
  CardSection,
  Button,
  Textarea,
  LoadingSpinner,
  Alert,
  EmptyState,
} from '../../shared/ui/index.js';
import { useParty } from '../../app/contexts/PartyContext/index.js';
import { useMonsterChat } from './hooks/useMonsterChat.js';

// Everything the monster says shares one voice
const monsterSpeechStyles = {
  fontSize: 'var(--font-size-lg)',
  lineHeight: 'var(--line-height-relaxed)',
  color: 'var(--color-text-primary)',
  fontFamily: 'var(--font-family-serif)',
  fontStyle: 'italic',
  whiteSpace: 'pre-wrap',
  margin: 0,
};

// The adventurer's words look plainer - spoken, not performed
const playerSpeechStyles = {
  fontSize: 'var(--font-size-md)',
  lineHeight: 'var(--line-height-relaxed)',
  color: 'var(--color-text-secondary)',
  whiteSpace: 'pre-wrap',
  margin: 0,
};

const speakerLabelStyles = {
  fontSize: 'var(--font-size-sm)',
  fontWeight: 'bold',
  color: 'var(--color-text-muted)',
  marginBottom: '4px',
};

/**
 * MonsterChatPanel component
 * @param {object|null} monster - The selected chat partner (clean monster object)
 */
function MonsterChatPanel({ monster }) {
  const {
    messages,
    hasMore,
    isLoadingHistory,
    isReplying,
    streamingText,
    error,
    memoryToasts,
    send,
    loadOlder,
  } = useMonsterChat(monster?.id || null);

  // The player speaks AS their character - their lines wear its name
  const { playerMonster } = useParty();
  const playerName = playerMonster?.name || 'You';

  const [draft, setDraft] = useState('');
  const threadEndRef = useRef(null);

  // Keep the newest words in view as they arrive
  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, streamingText]);

  if (!monster) {
    return (
      <Card size="xl" background="light">
        <CardSection type="content" alignment="center">
          <EmptyState
            size="lg"
            title="Sit down with a companion"
            description="Pick a monster to talk with. What you say to each other is remembered - and it changes them."
          />
        </CardSection>
      </Card>
    );
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!draft.trim() || isReplying) return;
    send(draft.trim());
    setDraft('');
  };

  return (
    <Card size="xl" background="light">
      <CardSection
        type="header"
        size="lg"
        title={`💬 Talking with ${monster.name}`}
        alignment="center"
      />

      {/* The thread */}
      <CardSection type="content">
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            maxWidth: '720px',
            margin: '0 auto',
          }}
        >
          {hasMore && (
            <div style={{ textAlign: 'center' }}>
              <Button size="sm" variant="secondary" onClick={loadOlder}>
                ⬆️ Earlier conversation
              </Button>
            </div>
          )}

          {isLoadingHistory && (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '16px' }}>
              <LoadingSpinner size="md" type="spin" />
            </div>
          )}

          {!isLoadingHistory && messages.length === 0 && !streamingText && (
            <p
              style={{ textAlign: 'center', color: 'var(--color-text-muted)', fontStyle: 'italic' }}
            >
              {monster.name} settles in beside you. Say something.
            </p>
          )}

          {messages.map((line) => {
            const isPlayer = line.role === 'player';
            return (
              <div key={line.id} style={{ textAlign: isPlayer ? 'right' : 'left' }}>
                <div style={speakerLabelStyles}>
                  {isPlayer ? `🧭 ${playerName}` : `👹 ${monster.name}`}
                </div>
                <p style={isPlayer ? playerSpeechStyles : monsterSpeechStyles}>"{line.text}"</p>
              </div>
            );
          })}

          {/* The reply, arriving token by token */}
          {isReplying && (
            <div style={{ textAlign: 'left' }}>
              <div style={speakerLabelStyles}>👹 {monster.name}</div>
              {streamingText ? (
                <p style={monsterSpeechStyles}>"{streamingText}"</p>
              ) : (
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    color: 'var(--color-text-muted)',
                    fontStyle: 'italic',
                  }}
                >
                  <LoadingSpinner size="sm" type="spin" />
                  {monster.name} considers your words...
                </div>
              )}
            </div>
          )}

          <div ref={threadEndRef} />
        </div>
      </CardSection>

      {/* Moments the monster decided to keep forever */}
      {memoryToasts.length > 0 && (
        <CardSection type="content" alignment="center">
          {memoryToasts.map((memory) => (
            <p
              key={memory.id}
              style={{
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-muted)',
                fontStyle: 'italic',
                margin: '4px 0',
              }}
            >
              ✨ {monster.name} will remember this: “{memory.content}”
            </p>
          ))}
        </CardSection>
      )}

      {error && (
        <CardSection type="content" alignment="center">
          <Alert type="error" size="md">
            {error}
          </Alert>
        </CardSection>
      )}

      {/* The adventurer speaks */}
      <CardSection type="content" alignment="center">
        <form
          onSubmit={handleSubmit}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            maxWidth: '640px',
            margin: '0 auto',
          }}
        >
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={`Talk with ${monster.name} - ask about its past, the last dungeon run, its dreams... it remembers what matters.`}
            rows={3}
          />
          <div>
            <Button
              size="md"
              variant="primary"
              type="submit"
              disabled={!draft.trim() || isReplying || isLoadingHistory}
            >
              {isReplying ? 'Listening...' : '💬 Speak'}
            </Button>
          </div>
        </form>
      </CardSection>
    </Card>
  );
}

export default MonsterChatPanel;
