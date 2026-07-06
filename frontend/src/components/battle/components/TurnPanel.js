// TurnPanel.js - One monster's turn: choose what it does
// Attack / Defend / Ability with targets, plus the player's own words:
// Custom Action (the referee judges if it's possible) and Talk
// (negotiate with the enemies - the LLM decides what comes of it)

import React from 'react';
import { Card, CardSection, Button, Select, Input, Textarea } from '../../../shared/ui/index.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';
import { useParty } from '../../../app/contexts/PartyContext/index.js';
import { useUsableItems } from '../../../app/hooks/useInventory.js';

const MODE_OPTIONS = [
  { value: 'attack', label: '⚔️ Attack' },
  { value: 'defend', label: '🛡️ Defend' },
  { value: 'ability', label: '⚡ Use Ability' },
  { value: 'item', label: '🎒 Use Item' },
  { value: 'custom', label: '✍️ Custom Action' },
  { value: 'talk', label: '💬 Talk' }
];

function TurnPanel() {
  const {
    displayedBattle,
    pendingActorId,
    pendingActorName,
    turnVanityText,
    currentSelection,
    isProcessing,
    outcome,
    updateSelection,
    executeTurn
  } = useBattleContext();
  const { partyMonsters } = useParty();
  const { items: usableItems } = useUsableItems();

  if (!pendingActorId || isProcessing || outcome) return null;

  const allies = displayedBattle?.allies || {};
  const enemies = displayedBattle?.enemies || {};
  const actorName = pendingActorName || allies[pendingActorId]?.name || 'Your monster';

  const actorMonster = (partyMonsters || []).find(m => String(m.id) === String(pendingActorId)) || null;

  const livingEnemyOptions = Object.entries(enemies)
    .filter(([, entry]) => entry.condition !== 'incapacitated' && !entry.fled)
    .map(([monsterId, entry]) => ({ value: monsterId, label: `👹 ${entry.name}` }));

  const allTargetOptions = [
    ...livingEnemyOptions,
    ...Object.entries(allies).map(([monsterId, entry]) => ({
      value: monsterId,
      label: `🛡️ ${entry.name}${entry.condition === 'incapacitated' ? ' (down)' : ''}`
    }))
  ];

  const abilityOptions = (actorMonster?.abilities || []).map(ability => ({
    value: String(ability.id),
    label: `⚡ ${ability.name}`
  }));

  const itemOptions = usableItems.map(item => ({
    value: String(item.id),
    label: `${item.emoji} ${item.name} (×${item.usesRemaining})`
  }));

  const mode = currentSelection.type || '';

  // Is the selection complete enough to execute?
  const isComplete = (() => {
    switch (mode) {
      case 'attack': return !!currentSelection.targetId;
      case 'defend': return true;
      case 'ability': return !!currentSelection.abilityId && !!currentSelection.targetId;
      case 'item': return !!currentSelection.itemId; // target optional - no target = itself
      case 'custom': return !!(currentSelection.text || '').trim();
      case 'talk': return !!(currentSelection.text || '').trim();
      default: return false;
    }
  })();

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="md" title={`✨ It's ${actorName}'s turn!`} alignment="center" />

      {/* The monster's streamed inner monologue - what it feels, thinks,
          and wants right now (the player still decides the action) */}
      {turnVanityText && (
        <CardSection type="content" alignment="center">
          <p style={{
            fontSize: 'var(--font-size-md)',
            lineHeight: 'var(--line-height-relaxed)',
            color: 'var(--color-text-secondary)',
            fontFamily: 'var(--font-family-serif)',
            fontStyle: 'italic',
            whiteSpace: 'pre-wrap',
            maxWidth: '640px',
            margin: '0 auto'
          }}>
            {turnVanityText}
          </p>
        </CardSection>
      )}

      <CardSection type="content">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '640px', margin: '0 auto' }}>

          {/* What kind of action? */}
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ minWidth: '90px', fontWeight: 'bold' }}>Action:</span>
            <div style={{ minWidth: '200px' }}>
              <Select
                options={MODE_OPTIONS}
                value={mode}
                placeholder="Choose an action..."
                onChange={(e) => updateSelection({ type: e.target.value, abilityId: null, itemId: null, targetId: null, text: '', info: '' })}
              />
            </div>
          </div>

          {/* Ability picker */}
          {mode === 'ability' && (
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ minWidth: '90px', fontWeight: 'bold' }}>Ability:</span>
              <div style={{ minWidth: '200px' }}>
                <Select
                  options={abilityOptions}
                  value={currentSelection.abilityId ? String(currentSelection.abilityId) : ''}
                  placeholder="Choose ability..."
                  onChange={(e) => updateSelection({ abilityId: Number(e.target.value) })}
                />
              </div>
            </div>
          )}

          {/* Item picker - one use is spent, and so is the turn */}
          {mode === 'item' && (
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ minWidth: '90px', fontWeight: 'bold' }}>Item:</span>
              <div style={{ minWidth: '200px' }}>
                <Select
                  options={itemOptions}
                  value={currentSelection.itemId ? String(currentSelection.itemId) : ''}
                  placeholder={itemOptions.length ? 'Choose item...' : 'No items in the inventory'}
                  onChange={(e) => updateSelection({ itemId: Number(e.target.value) })}
                />
              </div>
            </div>
          )}

          {/* Target picker */}
          {(mode === 'attack' || mode === 'ability' || mode === 'item' || mode === 'custom') && (
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ minWidth: '90px', fontWeight: 'bold' }}>Target:</span>
              <div style={{ minWidth: '200px' }}>
                <Select
                  options={mode === 'attack' ? livingEnemyOptions : allTargetOptions}
                  value={currentSelection.targetId || ''}
                  placeholder={
                    mode === 'custom' ? 'Optional target...'
                      : mode === 'item' ? `Optional target... (none = ${actorName})`
                        : 'Choose target...'
                  }
                  onChange={(e) => updateSelection({ targetId: e.target.value })}
                />
              </div>
            </div>
          )}

          {/* Custom action text */}
          {mode === 'custom' && (
            <>
              <Textarea
                value={currentSelection.text || ''}
                onChange={(e) => updateSelection({ text: e.target.value })}
                placeholder={`Describe what ${actorName} attempts... (the referee decides if it's possible - an impossible attempt wastes the turn)`}
                rows={3}
              />
              <Input
                value={currentSelection.info || ''}
                onChange={(e) => updateSelection({ info: e.target.value })}
                placeholder="Additional information (optional)"
              />
            </>
          )}

          {/* Talk text */}
          {mode === 'talk' && (
            <Textarea
              value={currentSelection.text || ''}
              onChange={(e) => updateSelection({ text: e.target.value })}
              placeholder="What does your party say to the enemies? Bargain, threaten, invite them to join you, plead for mercy..."
              rows={3}
            />
          )}
        </div>
      </CardSection>

      <CardSection type="content" alignment="center">
        <Button
          size="xl"
          icon="▶"
          variant="primary"
          disabled={!isComplete}
          onClick={executeTurn}
        >
          Take Turn
        </Button>
      </CardSection>
    </Card>
  );
}

export default TurnPanel;
