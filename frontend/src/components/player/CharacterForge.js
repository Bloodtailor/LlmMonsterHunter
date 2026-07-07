// CharacterForge.js - the finalize: answers become a character, live
// Queues create_player_character on mount and narrates its progress:
// workflowUpdate steps become stage labels, and the standard monster.*
// events fill the card in place as each stage lands (the same reveal
// the sanctuary uses). Completion hands the finished player up; failure
// offers a retry (the backend discards half-built characters itself).

import React, { useEffect, useRef, useState } from 'react';
import { Alert, Button, Card, CardSection, LoadingSpinner } from '../../shared/ui/index.js';
import { useEventSubscription } from '../../api/events/useEventSubscription.js';
import { transformMonster } from '../../api/transformers/monsters.js';
import * as playerApi from '../../api/services/player.js';
import MonsterCard from '../cards/MonsterCard.js';
import { FORGE_STEP_LABELS } from './creationSteps.js';

function CharacterForge({ choices, onForged }) {
  const [stepLabel, setStepLabel] = useState('Reading your answers...');
  const [liveMonster, setLiveMonster] = useState(null);
  const [error, setError] = useState(null);

  const workflowIdRef = useRef(null);
  const startedRef = useRef(false);

  const begin = async () => {
    setError(null);
    setStepLabel('Reading your answers...');
    try {
      const result = await playerApi.createCharacter(choices);
      if (!result.success || !result.workflowId) {
        setError(result.error || 'The forge would not light - try again.');
        return;
      }
      workflowIdRef.current = result.workflowId;
    } catch (requestError) {
      setError(requestError.message || 'The forge would not light - try again.');
    }
  };

  useEffect(() => {
    if (!startedRef.current) {
      startedRef.current = true;
      begin();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEventSubscription('workflowUpdate', ({ workflowId, step }) => {
    if (workflowId !== workflowIdRef.current) return;
    if (FORGE_STEP_LABELS[step]) setStepLabel(FORGE_STEP_LABELS[step]);
  });

  // The forge is the only thing creating monsters while this screen is
  // up - monster.* events during it describe OUR character taking shape
  useEventSubscription('monsterCreated', ({ monster }) => {
    if (workflowIdRef.current && monster) setLiveMonster(monster);
  });
  useEventSubscription('monsterUpdated', ({ monster }) => {
    if (workflowIdRef.current && monster && (!liveMonster || monster.id === liveMonster.id)) {
      setLiveMonster(monster);
    }
  });
  useEventSubscription('monsterAbilityAdded', ({ monsterId, ability }) => {
    if (!workflowIdRef.current || !ability) return;
    setLiveMonster((current) =>
      current && current.id === monsterId
        ? {
            ...current,
            abilities: [...(current.abilities || []), ability],
            abilityCount: (current.abilityCount || 0) + 1,
          }
        : current,
    );
  });

  useEventSubscription('workflowCompleted', ({ workflowId, result }) => {
    if (workflowId !== workflowIdRef.current) return;
    workflowIdRef.current = null;
    const finished = result?.monster ? transformMonster(result.monster) : liveMonster;
    onForged(finished);
  });

  useEventSubscription('workflowFailed', ({ workflowId, error: failure }) => {
    if (workflowId !== workflowIdRef.current) return;
    workflowIdRef.current = null;
    setError(
      (typeof failure === 'object' ? failure?.error : failure) ||
        'The forge went cold - try again.',
    );
  });

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="lg" title="⚒️ Taking shape" alignment="center">
        {!error && (
          <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
            <LoadingSpinner size="sm" type="spin" /> {stepLabel}
          </p>
        )}
      </CardSection>

      <CardSection type="content" alignment="center" padding="lg">
        {error ? (
          <div
            style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' }}
          >
            <Alert type="error" title="Creation failed">
              {String(error)}
            </Alert>
            <Button size="lg" variant="primary" onClick={begin}>
              Try again
            </Button>
          </div>
        ) : liveMonster ? (
          <MonsterCard monster={liveMonster} size="lg" hideFlipHint={false} />
        ) : (
          <p style={{ color: 'var(--color-text-secondary)' }}>The first lines are being drawn...</p>
        )}
      </CardSection>
    </Card>
  );
}

export default CharacterForge;
