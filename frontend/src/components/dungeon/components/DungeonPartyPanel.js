// DungeonPartyPanel.js - The party, always visible while in the dungeon
// Shows every party monster with its run condition, and lets any monster
// use any of its abilities on ANYTHING - a path, a monster, the location,
// or something the player describes. The LLM referee decides if it does
// anything at all. (During battles, abilities cost a turn instead.)

import React, { useState } from 'react';
import { Card, CardSection, Button, Select, Input, Badge, LoadingSpinner } from '../../../shared/ui/index.js';
import { useParty } from '../../../app/contexts/PartyContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';

// Condition colors along the ladder (fresh -> incapacitated)
const CONDITION_VARIANTS = {
  fresh: 'success',
  scuffed: 'info',
  wounded: 'warning',
  battered: 'warning',
  critical: 'error',
  incapacitated: 'error'
};

/**
 * DungeonPartyPanel component
 * Party status + the free-form ability form for dungeon exploration
 */
function DungeonPartyPanel() {
  const { partyMonsters } = useParty();
  const {
    partyConditions,
    paths,
    encounterMonsters,
    isUsingAbility,
    abilityResult,
    activateAbility,
    exitText
  } = useDungeon();
  const { displayedBattle } = useBattleContext();

  const [actorId, setActorId] = useState('');
  const [abilityId, setAbilityId] = useState('');
  const [targetValue, setTargetValue] = useState('');
  const [customTarget, setCustomTarget] = useState('');

  if (exitText) return null;
  if (!partyMonsters || partyMonsters.length === 0) return null;

  // During a battle, abilities are used on the monster's turn instead
  const battleInProgress = !!displayedBattle?.in_battle;

  const actorMonster = partyMonsters.find(m => String(m.id) === actorId) || null;

  const actorOptions = partyMonsters.map(monster => ({
    value: String(monster.id),
    label: `🛡️ ${monster.name}`
  }));

  const abilityOptions = (actorMonster?.abilities || []).map(ability => ({
    value: String(ability.id),
    label: `⚡ ${ability.name}`
  }));

  // Targets: anything and anyone. Values encode the target type.
  const targetOptions = [
    { value: 'location', label: '📍 This location' },
    ...partyMonsters.map(monster => ({
      value: `party:${monster.id}`,
      label: `🛡️ ${monster.name}`
    })),
    ...(encounterMonsters || []).map(monster => ({
      value: `monster:${monster.id}`,
      label: `👹 ${monster.name}`
    })),
    ...Object.entries(paths || {}).map(([pathId, path]) => ({
      value: `path:${pathId}`,
      label: `🧭 ${path.name || pathId}`
    })),
    { value: 'custom', label: '✍️ Something else...' }
  ];

  const isComplete = !!actorId && !!abilityId && !!targetValue &&
    (targetValue !== 'custom' || !!customTarget.trim());

  const handleUseAbility = () => {
    if (!isComplete || isUsingAbility) return;

    // Decode the selected target into the API's shape
    let targetType = 'location';
    let targetId = null;
    let targetText = '';

    if (targetValue.startsWith('party:')) {
      targetType = 'monster';
      targetId = Number(targetValue.slice('party:'.length));
    } else if (targetValue.startsWith('monster:')) {
      targetType = 'monster';
      targetId = Number(targetValue.slice('monster:'.length));
    } else if (targetValue.startsWith('path:')) {
      targetType = 'path';
      targetId = targetValue.slice('path:'.length);
    } else if (targetValue === 'custom') {
      targetType = 'custom';
      targetText = customTarget.trim();
    }

    activateAbility({
      monsterId: Number(actorId),
      abilityId: Number(abilityId),
      targetType,
      targetId,
      targetText
    });
  };

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="md" title="🛡️ Your Party" alignment="center" />

      {/* Every member, with their condition for this run */}
      <CardSection type="content">
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {partyMonsters.map(monster => {
            const condition = partyConditions?.[String(monster.id)] || 'fresh';
            return (
              <div
                key={monster.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '6px',
                  minWidth: '140px',
                  padding: '12px',
                  borderRadius: '8px',
                  background: 'var(--color-surface-secondary, rgba(0,0,0,0.15))'
                }}
              >
                <span style={{ fontWeight: 'bold', color: 'var(--color-text-primary)' }}>{monster.name}</span>
                <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)' }}>{monster.species}</span>
                <Badge variant={CONDITION_VARIANTS[condition] || 'info'} size="sm" pill>
                  {condition}
                </Badge>
              </div>
            );
          })}
        </div>
      </CardSection>

      {/* The free-form ability form - anything, on anything */}
      {battleInProgress ? (
        <CardSection type="content" alignment="center">
          <p style={{ color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
            ⚔️ In battle, abilities are used on each monster's turn.
          </p>
        </CardSection>
      ) : (
        <CardSection type="content">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '640px', margin: '0 auto' }}>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
              <div style={{ minWidth: '180px' }}>
                <Select
                  options={actorOptions}
                  value={actorId}
                  placeholder="Monster..."
                  onChange={(e) => {
                    setActorId(e.target.value);
                    setAbilityId('');
                  }}
                />
              </div>
              <div style={{ minWidth: '180px' }}>
                <Select
                  options={abilityOptions}
                  value={abilityId}
                  placeholder="Ability..."
                  onChange={(e) => setAbilityId(e.target.value)}
                />
              </div>
              <div style={{ minWidth: '180px' }}>
                <Select
                  options={targetOptions}
                  value={targetValue}
                  placeholder="Target anything..."
                  onChange={(e) => setTargetValue(e.target.value)}
                />
              </div>
            </div>

            {targetValue === 'custom' && (
              <Input
                value={customTarget}
                onChange={(e) => setCustomTarget(e.target.value)}
                placeholder="Describe the target... (the referee decides if the ability does anything at all)"
              />
            )}

            <div style={{ textAlign: 'center' }}>
              <Button
                size="md"
                icon="⚡"
                variant="primary"
                disabled={!isComplete || isUsingAbility}
                onClick={handleUseAbility}
              >
                {isUsingAbility ? (
                  <>
                    <span style={{ marginRight: '8px' }}><LoadingSpinner size="sm" type="spin" /></span>
                    Using ability...
                  </>
                ) : (
                  'Use Ability'
                )}
              </Button>
            </div>

            {/* The referee's narration of what came of it */}
            {abilityResult && (
              <p style={{
                fontSize: 'var(--font-size-md)',
                lineHeight: 'var(--line-height-relaxed)',
                color: 'var(--color-text-primary)',
                fontFamily: 'var(--font-family-serif)',
                fontStyle: 'italic',
                textAlign: 'center',
                whiteSpace: 'pre-wrap'
              }}>
                {abilityResult.narration}
              </p>
            )}
          </div>
        </CardSection>
      )}
    </Card>
  );
}

export default DungeonPartyPanel;
