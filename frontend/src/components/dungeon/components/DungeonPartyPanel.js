// DungeonPartyPanel.js - The party, always visible while in the dungeon
// Shows the party's ACTUAL monster cards (flip/expand like everywhere else)
// with each member's run condition, toggleable to the inventory view.
// Any monster can use any ability - and the party can use any item - on
// ANYTHING: a path, a monster, the location, or something the player
// describes. The LLM referee decides if it does anything at all.
// (During battles, abilities and items cost a turn instead.)

import React, { useState } from 'react';
import {
  Card,
  CardSection,
  Button,
  Select,
  Input,
  Badge,
  LoadingSpinner,
} from '../../../shared/ui/index.js';
import { useParty } from '../../../app/contexts/PartyContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/useDungeon.js';
import { useBattleContext } from '../../../app/contexts/BattleContext/index.js';
import { useMonsterCardViewer } from '../../cards/useMonsterCardViewer.js';
import { useUsableItems } from '../../../app/hooks/useInventory.js';
import InventoryPanel from '../../inventory/InventoryPanel.js';
import ResourceBadges from '../../battle/components/ResourceBadges.js';

// Condition colors along the ladder (fresh -> incapacitated)
const CONDITION_VARIANTS = {
  fresh: 'success',
  scuffed: 'info',
  wounded: 'warning',
  battered: 'warning',
  critical: 'error',
  incapacitated: 'error',
};

const narrationStyles = {
  fontSize: 'var(--font-size-md)',
  lineHeight: 'var(--line-height-relaxed)',
  color: 'var(--color-text-primary)',
  fontFamily: 'var(--font-family-serif)',
  fontStyle: 'italic',
  textAlign: 'center',
  whiteSpace: 'pre-wrap',
};

/**
 * DungeonPartyPanel component
 * Party cards + free-form ability/item forms, or the inventory view
 */
function DungeonPartyPanel() {
  const { partyMonsters } = useParty();
  const {
    partyConditions,
    partyResources,
    paths,
    encounterMonsters,
    isUsingAbility,
    abilityResult,
    activateAbility,
    isUsingItem,
    itemResult,
    activateItem,
    exitText,
  } = useDungeon();
  const { displayedBattle } = useBattleContext();
  const { MonsterCard, viewer } = useMonsterCardViewer();
  const { items: usableItems } = useUsableItems();

  const [view, setView] = useState('party'); // 'party' | 'inventory'

  // Ability form state
  const [actorId, setActorId] = useState('');
  const [abilityId, setAbilityId] = useState('');
  const [targetValue, setTargetValue] = useState('');
  const [customTarget, setCustomTarget] = useState('');

  // Item form state
  const [itemId, setItemId] = useState('');
  const [itemTargetValue, setItemTargetValue] = useState('');
  const [itemCustomTarget, setItemCustomTarget] = useState('');

  if (exitText) return null;
  if (!partyMonsters || partyMonsters.length === 0) return null;

  // During a battle, abilities and items are used on the monster's turn
  const battleInProgress = !!displayedBattle?.in_battle;

  const actorMonster = partyMonsters.find((m) => String(m.id) === actorId) || null;

  const actorOptions = partyMonsters.map((monster) => ({
    value: String(monster.id),
    label: `🛡️ ${monster.name}`,
  }));

  const abilityOptions = (actorMonster?.abilities || []).map((ability) => ({
    value: String(ability.id),
    label: `⚡ ${ability.name}`,
  }));

  const itemOptions = usableItems.map((item) => ({
    value: String(item.id),
    label: `${item.emoji} ${item.name} (×${item.usesRemaining})`,
  }));

  // Targets: anything and anyone. Values encode the target type.
  const targetOptions = [
    { value: 'location', label: '📍 This location' },
    ...partyMonsters.map((monster) => ({
      value: `party:${monster.id}`,
      label: `🛡️ ${monster.name}`,
    })),
    ...(encounterMonsters || []).map((monster) => ({
      value: `monster:${monster.id}`,
      label: `👹 ${monster.name}`,
    })),
    ...Object.entries(paths || {}).map(([pathId, path]) => ({
      value: `path:${pathId}`,
      label: `🧭 ${path.name || pathId}`,
    })),
    { value: 'custom', label: '✍️ Something else...' },
  ];

  // Decode a target-select value into the API's shape
  const decodeTarget = (value, customText) => {
    let targetType = 'location';
    let targetId = null;
    let targetText = '';

    if (value.startsWith('party:')) {
      targetType = 'monster';
      targetId = Number(value.slice('party:'.length));
    } else if (value.startsWith('monster:')) {
      targetType = 'monster';
      targetId = Number(value.slice('monster:'.length));
    } else if (value.startsWith('path:')) {
      targetType = 'path';
      targetId = value.slice('path:'.length);
    } else if (value === 'custom') {
      targetType = 'custom';
      targetText = customText.trim();
    }

    return { targetType, targetId, targetText };
  };

  const isAbilityComplete =
    !!actorId &&
    !!abilityId &&
    !!targetValue &&
    (targetValue !== 'custom' || !!customTarget.trim());

  const isItemComplete =
    !!itemId && !!itemTargetValue && (itemTargetValue !== 'custom' || !!itemCustomTarget.trim());

  const handleUseAbility = () => {
    if (!isAbilityComplete || isUsingAbility) return;
    const target = decodeTarget(targetValue, customTarget);
    activateAbility({
      monsterId: Number(actorId),
      abilityId: Number(abilityId),
      ...target,
    });
  };

  const handleUseItem = () => {
    if (!isItemComplete || isUsingItem) return;
    const target = decodeTarget(itemTargetValue, itemCustomTarget);
    activateItem({
      itemId: Number(itemId),
      ...target,
    });
    setItemId('');
  };

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="md" title="🛡️ Your Party" alignment="center">
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
          <Button
            size="sm"
            icon="🛡️"
            variant={view === 'party' ? 'primary' : 'secondary'}
            onClick={() => setView('party')}
          >
            Party
          </Button>
          <Button
            size="sm"
            icon="🎒"
            variant={view === 'inventory' ? 'primary' : 'secondary'}
            onClick={() => setView('inventory')}
          >
            Inventory
          </Button>
        </div>
      </CardSection>

      {view === 'inventory' ? (
        <CardSection type="content">
          <InventoryPanel />
        </CardSection>
      ) : (
        <>
          {/* Every member as their real card, with their condition for this run */}
          <CardSection type="content">
            <div
              style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}
            >
              {partyMonsters.map((monster) => {
                const condition = partyConditions?.[String(monster.id)] || 'fresh';
                const pools = partyResources?.[String(monster.id)] || {};
                return (
                  <div
                    key={monster.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <MonsterCard
                      monster={monster}
                      size="sm"
                      showPartyToggle={false}
                      hideFlipHint={true}
                    />
                    <Badge variant={CONDITION_VARIANTS[condition] || 'info'} size="sm" pill>
                      {condition}
                    </Badge>
                    <ResourceBadges stamina={pools.stamina} mana={pools.mana} />
                  </div>
                );
              })}
            </div>
          </CardSection>

          {battleInProgress ? (
            <CardSection type="content" alignment="center">
              <p style={{ color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
                ⚔️ In battle, abilities and items are used on each monster's turn.
              </p>
            </CardSection>
          ) : (
            <>
              {/* The free-form ability form - anything, on anything */}
              <CardSection type="content">
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                    maxWidth: '640px',
                    margin: '0 auto',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      gap: '12px',
                      flexWrap: 'wrap',
                      justifyContent: 'center',
                    }}
                  >
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
                      disabled={!isAbilityComplete || isUsingAbility}
                      onClick={handleUseAbility}
                    >
                      {isUsingAbility ? (
                        <>
                          <span style={{ marginRight: '8px' }}>
                            <LoadingSpinner size="sm" type="spin" />
                          </span>
                          Using ability...
                        </>
                      ) : (
                        'Use Ability'
                      )}
                    </Button>
                  </div>

                  {/* The referee's narration of what came of it */}
                  {abilityResult && <p style={narrationStyles}>{abilityResult.narration}</p>}
                </div>
              </CardSection>

              {/* The item form - the party's inventory, on anything */}
              {itemOptions.length > 0 && (
                <CardSection type="content">
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '12px',
                      maxWidth: '640px',
                      margin: '0 auto',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        gap: '12px',
                        flexWrap: 'wrap',
                        justifyContent: 'center',
                      }}
                    >
                      <div style={{ minWidth: '220px' }}>
                        <Select
                          options={itemOptions}
                          value={itemId}
                          placeholder="Item..."
                          onChange={(e) => setItemId(e.target.value)}
                        />
                      </div>
                      <div style={{ minWidth: '180px' }}>
                        <Select
                          options={targetOptions}
                          value={itemTargetValue}
                          placeholder="Target anything..."
                          onChange={(e) => setItemTargetValue(e.target.value)}
                        />
                      </div>
                    </div>

                    {itemTargetValue === 'custom' && (
                      <Input
                        value={itemCustomTarget}
                        onChange={(e) => setItemCustomTarget(e.target.value)}
                        placeholder="Describe the target... (one use is spent regardless of the outcome)"
                      />
                    )}

                    <div style={{ textAlign: 'center' }}>
                      <Button
                        size="md"
                        icon="🎒"
                        variant="primary"
                        disabled={!isItemComplete || isUsingItem}
                        onClick={handleUseItem}
                      >
                        {isUsingItem ? (
                          <>
                            <span style={{ marginRight: '8px' }}>
                              <LoadingSpinner size="sm" type="spin" />
                            </span>
                            Using item...
                          </>
                        ) : (
                          'Use Item'
                        )}
                      </Button>
                    </div>

                    {itemResult && <p style={narrationStyles}>{itemResult.narration}</p>}
                  </div>
                </CardSection>
              )}
            </>
          )}
        </>
      )}

      {viewer}
    </Card>
  );
}

export default DungeonPartyPanel;
