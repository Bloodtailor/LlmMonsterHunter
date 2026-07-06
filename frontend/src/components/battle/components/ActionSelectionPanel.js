// ActionSelectionPanel.js - Choose each party monster's action for the round
// One row per able ally: action (Attack / Defend / their abilities) + target
// Execute queues the round; after that the player can't change anything

import React from 'react';
import { Card, CardSection, Button, Select } from '../../../shared/ui/index.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';
import { useParty } from '../../../app/contexts/PartyContext/index.js';

function ActionSelectionPanel() {
  const {
    displayedBattle,
    selectedActions,
    isProcessing,
    outcome,
    setMonsterAction,
    executeRound
  } = useBattleContext();
  const { partyMonsters } = useParty();

  // Only during action selection
  if (!displayedBattle?.in_battle || isProcessing || outcome) return null;

  const allies = displayedBattle.allies || {};
  const enemies = displayedBattle.enemies || {};

  const ableAllies = Object.entries(allies).filter(
    ([, entry]) => entry.condition !== 'incapacitated'
  );
  if (ableAllies.length === 0) return null;

  const livingEnemyOptions = Object.entries(enemies)
    .filter(([, entry]) => entry.condition !== 'incapacitated')
    .map(([monsterId, entry]) => ({ value: monsterId, label: `👹 ${entry.name}` }));

  // Abilities may target anyone - allies (support/heals, even fallen ones) or enemies
  const allTargetOptions = [
    ...livingEnemyOptions,
    ...Object.entries(allies).map(([monsterId, entry]) => ({
      value: monsterId,
      label: `🛡️ ${entry.name}${entry.condition === 'incapacitated' ? ' (down)' : ''}`
    }))
  ];

  const findPartyMonster = (monsterId) =>
    (partyMonsters || []).find(m => String(m.id) === String(monsterId)) || null;

  // Build the action dropdown for one ally
  const actionOptionsFor = (monsterId) => {
    const monster = findPartyMonster(monsterId);
    const abilityOptions = (monster?.abilities || []).map(ability => ({
      value: `ability:${ability.id}`,
      label: `⚡ ${ability.name}`
    }));
    return [
      { value: 'attack', label: '⚔️ Attack' },
      { value: 'defend', label: '🛡️ Defend' },
      ...abilityOptions
    ];
  };

  const selectionFor = (monsterId) => selectedActions[monsterId] || {};

  const handleActionChange = (monsterId, rawValue) => {
    if (rawValue.startsWith('ability:')) {
      setMonsterAction(monsterId, {
        action: 'ability',
        abilityId: Number(rawValue.split(':')[1]),
        targetId: null
      });
    } else {
      setMonsterAction(monsterId, { action: rawValue, abilityId: null, targetId: null });
    }
  };

  const handleTargetChange = (monsterId, targetId) => {
    setMonsterAction(monsterId, { ...selectionFor(monsterId), targetId });
  };

  // Round is ready when every able ally has a complete action
  const isComplete = ableAllies.every(([monsterId]) => {
    const selection = selectionFor(monsterId);
    if (!selection.action) return false;
    if (selection.action === 'defend') return true;
    return !!selection.targetId;
  });

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="md" title={`⚔️ Round ${displayedBattle.round} - Choose Your Actions`} alignment="center" />

      <CardSection type="content">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '640px', margin: '0 auto' }}>
          {ableAllies.map(([monsterId, entry]) => {
            const selection = selectionFor(monsterId);
            const rawActionValue = selection.action === 'ability'
              ? `ability:${selection.abilityId}`
              : (selection.action || '');
            const needsTarget = selection.action && selection.action !== 'defend';

            return (
              <div key={monsterId} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{ minWidth: '140px', fontWeight: 'bold' }}>{entry.name}</span>
                <div style={{ minWidth: '180px' }}>
                  <Select
                    options={actionOptionsFor(monsterId)}
                    value={rawActionValue}
                    placeholder="Choose action..."
                    onChange={(e) => handleActionChange(monsterId, e.target.value)}
                  />
                </div>
                {needsTarget && (
                  <div style={{ minWidth: '180px' }}>
                    <Select
                      options={selection.action === 'attack' ? livingEnemyOptions : allTargetOptions}
                      value={selection.targetId || ''}
                      placeholder="Choose target..."
                      onChange={(e) => handleTargetChange(monsterId, e.target.value)}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardSection>

      <CardSection type="content" alignment="center">
        <Button
          size="xl"
          icon="⚔️"
          variant="primary"
          disabled={!isComplete}
          onClick={executeRound}
        >
          Execute!
        </Button>
      </CardSection>
    </Card>
  );
}

export default ActionSelectionPanel;
