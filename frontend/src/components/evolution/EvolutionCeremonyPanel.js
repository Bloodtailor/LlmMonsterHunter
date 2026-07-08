// EvolutionCeremonyPanel.js - The altar itself, for one chosen companion
// idle: the companion's card, an optional guidance whisper, and the Begin
// button. evolving: the card flips live as monster.evolved lands (explosion),
// the ceremony narration streams in, and a step line tracks the workflow.
// complete: an old->new summary strip (the before-snapshot vs the live
// card), the saved narrative, and the art reveal (second explosion).

import React, { useEffect, useState } from 'react';
import {
  Card,
  CardSection,
  Button,
  Alert,
  Textarea,
  LoadingSpinner,
  EmptyState,
} from '../../shared/ui/index.js';
import MonsterCard from '../cards/MonsterCard.js';
import HueBasedExplosion from '../../shared/ui/Explosion/HueBasedExplosion.js';
import EvolutionLineage from './EvolutionLineage.js';
import { useMonsterEvolution, EVOLUTION_STEP_LABELS } from './hooks/useMonsterEvolution.js';
import { getCardArtUrl } from '../../api/services/monster.js';

const GUIDANCE_MAX_CHARS = 200;

// One "HP 100 -> 125" line for the summary strip
function StatDelta({ label, before, after }) {
  const grew = Number(after) > Number(before);
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        gap: '12px',
        fontSize: 'var(--font-size-sm)',
      }}
    >
      <span style={{ color: 'var(--color-text-muted)' }}>{label}</span>
      <span>
        {before}
        <span style={{ color: 'var(--color-text-muted)' }}> → </span>
        <span
          style={{
            color: grew ? 'var(--color-success, #3fb950)' : 'var(--color-text-primary)',
            fontWeight: 'bold',
          }}
        >
          {after}
        </span>
      </span>
    </div>
  );
}

// An explosion centered over whatever it overlays
function BurstOverlay({ active, hue, onDone }) {
  if (!active) return null;
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
        zIndex: 5,
      }}
    >
      <HueBasedExplosion hue={hue} size="xl" intensity={1.5} onComplete={onDone} />
    </div>
  );
}

/**
 * EvolutionCeremonyPanel component
 * @param {object|null} monster - The chosen companion (LIVE object - PartyContext
 *   patches it in place as the ceremony's SSE events land)
 */
function EvolutionCeremonyPanel({ monster }) {
  const {
    phase,
    currentStep,
    narration,
    beforeSnapshot,
    evolution,
    result,
    artRevealed,
    error,
    begin,
    reset,
  } = useMonsterEvolution(monster);

  const [guidance, setGuidance] = useState('');
  const [transformBurst, setTransformBurst] = useState(false);
  const [artBurst, setArtBurst] = useState(false);

  // Fresh companion, fresh whisper
  useEffect(() => {
    setGuidance('');
    setTransformBurst(false);
    setArtBurst(false);
  }, [monster?.id]);

  // The transform moment and the art reveal each get their burst
  useEffect(() => {
    if (evolution) setTransformBurst(true);
  }, [evolution]);
  useEffect(() => {
    if (artRevealed) setArtBurst(true);
  }, [artRevealed]);

  if (!monster) {
    return (
      <Card size="lg" background="light">
        <CardSection type="content" alignment="center">
          <EmptyState
            size="lg"
            title="The altar waits"
            description="Choose a companion to bring before the altar. Evolution is the big leap - everything it has lived shapes what it becomes."
          />
        </CardSection>
      </Card>
    );
  }

  const stepLabel = EVOLUTION_STEP_LABELS[currentStep] || 'The ceremony continues';
  const oldArt = evolution ? getCardArtUrl(evolution.oldCardArtPath) : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <Card size="lg" background="light">
        <CardSection
          type="header"
          size="md"
          title={
            phase === 'complete'
              ? `⬆️ ${monster.name} has evolved`
              : `⬆️ The Altar — ${monster.name}`
          }
          alignment="center"
        />
        <CardSection type="content">
          <div
            style={{ display: 'flex', flexDirection: 'column', gap: '20px', alignItems: 'center' }}
          >
            {/* The card, live-patched as the ceremony lands; bursts overlay it */}
            <div style={{ position: 'relative' }}>
              <MonsterCard monster={monster} size="lg" hideFlipHint={phase === 'evolving'} />
              <BurstOverlay
                active={transformBurst}
                hue="purple"
                onDone={() => setTransformBurst(false)}
              />
              <BurstOverlay active={artBurst} hue="yellow" onDone={() => setArtBurst(false)} />
            </div>

            {/* ===== IDLE: the whisper and the leap ===== */}
            {phase === 'idle' && (
              <div
                style={{
                  width: '100%',
                  maxWidth: '520px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <Textarea
                  value={guidance}
                  onChange={(event) => setGuidance(event.target.value)}
                  placeholder={`Whisper a direction for ${monster.name}'s evolution (optional) — e.g. "lean into the storm magic". Leave blank and its history decides.`}
                  rows={3}
                  maxLength={GUIDANCE_MAX_CHARS}
                />
                <div
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-text-muted)',
                    textAlign: 'right',
                  }}
                >
                  {guidance.length}/{GUIDANCE_MAX_CHARS}
                </div>
                <Button size="lg" icon="⬆️" variant="primary" onClick={() => begin(guidance)}>
                  Begin the Evolution
                </Button>
                <p
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-text-muted)',
                    textAlign: 'center',
                    margin: 0,
                  }}
                >
                  Evolution is permanent. {monster.name} keeps every memory, bond, and ability — and
                  becomes something more.
                </p>
              </div>
            )}

            {/* ===== EVOLVING: the step line and the streaming story ===== */}
            {phase === 'evolving' && (
              <div
                style={{
                  width: '100%',
                  maxWidth: '560px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    justifyContent: 'center',
                    color: 'var(--color-text-secondary)',
                  }}
                >
                  <LoadingSpinner size="sm" type="spin" />
                  <span>{stepLabel}...</span>
                </div>
                {narration && (
                  <div
                    style={{
                      fontStyle: 'italic',
                      color: 'var(--color-text-secondary)',
                      lineHeight: 1.6,
                      background: 'var(--color-background-medium)',
                      borderRadius: '10px',
                      padding: '14px 16px',
                      maxHeight: '220px',
                      overflowY: 'auto',
                    }}
                  >
                    {narration}
                  </div>
                )}
              </div>
            )}

            {/* ===== COMPLETE: what it was, what it became ===== */}
            {phase === 'complete' && (
              <div
                style={{
                  width: '100%',
                  maxWidth: '560px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '16px',
                }}
              >
                {evolution && beforeSnapshot && (
                  <div
                    style={{
                      display: 'flex',
                      gap: '16px',
                      alignItems: 'center',
                      background: 'var(--color-background-medium)',
                      borderRadius: '10px',
                      padding: '14px 16px',
                    }}
                  >
                    {oldArt && (
                      <img
                        src={oldArt}
                        alt={evolution.oldName}
                        style={{
                          width: '64px',
                          height: '64px',
                          borderRadius: '8px',
                          objectFit: 'cover',
                          flexShrink: 0,
                          opacity: 0.75,
                        }}
                      />
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 'bold' }}>
                        {evolution.oldName} the {evolution.oldSpecies}
                        <span style={{ color: 'var(--color-text-muted)' }}> → </span>
                        {evolution.newName} the {evolution.newSpecies}
                      </div>
                      <div
                        style={{
                          fontSize: 'var(--font-size-sm)',
                          color: 'var(--color-text-muted)',
                        }}
                      >
                        Stage {evolution.stage} · {evolution.oldRarity || 'common'} →{' '}
                        {evolution.newRarity}
                      </div>
                      <div
                        style={{
                          marginTop: '8px',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '2px',
                        }}
                      >
                        <StatDelta
                          label="Health"
                          before={beforeSnapshot.stats?.maxHealth}
                          after={monster.stats?.maxHealth}
                        />
                        <StatDelta
                          label="Attack"
                          before={beforeSnapshot.stats?.attack}
                          after={monster.stats?.attack}
                        />
                        <StatDelta
                          label="Defense"
                          before={beforeSnapshot.stats?.defense}
                          after={monster.stats?.defense}
                        />
                        <StatDelta
                          label="Speed"
                          before={beforeSnapshot.stats?.speed}
                          after={monster.stats?.speed}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {(result?.new_ability || (result?.reworded_abilities || []).length > 0) && (
                  <div
                    style={{
                      fontSize: 'var(--font-size-sm)',
                      color: 'var(--color-text-secondary)',
                      textAlign: 'center',
                    }}
                  >
                    {result?.new_ability && (
                      <div>
                        ✨ New signature ability: <strong>{result.new_ability.name}</strong>
                      </div>
                    )}
                    {(result?.reworded_abilities || []).length > 0 && (
                      <div>
                        🔁 Evolved abilities: {(result.reworded_abilities || []).join(', ')}
                      </div>
                    )}
                    {result?.art_regenerated === false && (
                      <div style={{ color: 'var(--color-text-muted)' }}>
                        Its old portrait stands, for now.
                      </div>
                    )}
                  </div>
                )}

                {narration && (
                  <div
                    style={{
                      fontStyle: 'italic',
                      color: 'var(--color-text-secondary)',
                      lineHeight: 1.6,
                      background: 'var(--color-background-medium)',
                      borderRadius: '10px',
                      padding: '14px 16px',
                      maxHeight: '260px',
                      overflowY: 'auto',
                    }}
                  >
                    {narration}
                  </div>
                )}

                <Button size="md" icon="⬆️" variant="secondary" onClick={reset}>
                  Approach the altar again
                </Button>
              </div>
            )}

            {/* ===== FAILED ===== */}
            {phase === 'failed' && (
              <div
                style={{
                  width: '100%',
                  maxWidth: '520px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <Alert type="error" size="md">
                  {error || 'The evolution faltered.'}
                </Alert>
                <Button size="md" icon="⬆️" variant="secondary" onClick={reset}>
                  Try again
                </Button>
              </div>
            )}
          </div>
        </CardSection>
      </Card>

      <EvolutionLineage monsterId={monster.id} refreshToken={phase} />
    </div>
  );
}

export default EvolutionCeremonyPanel;
