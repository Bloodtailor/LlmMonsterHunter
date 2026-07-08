// MonsterChatPicker.js - Choose which following monster to talk with
// Compact selectable rows (art thumbnail + name + species) built from the
// PartyContext's following list - every recruited monster can chat.

import React from 'react';
import { Card, CardSection, EmptyState, LoadingSpinner } from '../../shared/ui/index.js';
import { useParty } from '../../app/contexts/PartyContext/index.js';
import { getCardArtUrl } from '../../api/services/monster.js';

function partnerArtUrl(monster) {
  if (!monster?.cardArt?.exists) return null;
  return getCardArtUrl(monster.cardArt.relativePath);
}

/**
 * MonsterChatPicker component - also reused by other home-base screens
 * (the Evolution Altar) that need "pick one of your companions"
 * @param {number|null} selectedId - Currently selected partner
 * @param {function} onSelect - Called with a monster object when picked
 * @param {string} [title] - Picker heading
 * @param {string} [emptyTitle] - Heading when no one follows yet
 * @param {string} [emptyDescription] - Body when no one follows yet
 */
function MonsterChatPicker({
  selectedId,
  onSelect,
  title = '🐾 Your companions',
  emptyTitle = 'No one to talk to yet',
  emptyDescription = 'Monsters that join you in the dungeon will gather here, ready to talk.',
}) {
  const { followingMonsters, loadingFollowers } = useParty();

  const rowStyles = (isSelected) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    width: '100%',
    padding: '10px 12px',
    border: isSelected
      ? '2px solid var(--color-primary)'
      : '2px solid var(--color-border, transparent)',
    borderRadius: '10px',
    background: isSelected ? 'var(--color-background-medium)' : 'var(--color-background-light)',
    cursor: 'pointer',
    textAlign: 'left',
  });

  const thumbStyles = {
    width: '44px',
    height: '44px',
    borderRadius: '8px',
    objectFit: 'cover',
    flexShrink: 0,
    background: 'var(--color-background-dark)',
  };

  return (
    <Card size="lg" background="light">
      <CardSection type="header" size="md" title={title} alignment="center" />
      <CardSection type="content">
        {loadingFollowers && (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '16px' }}>
            <LoadingSpinner size="md" type="spin" />
          </div>
        )}

        {!loadingFollowers && (!followingMonsters || followingMonsters.length === 0) && (
          <EmptyState size="md" title={emptyTitle} description={emptyDescription} />
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {(followingMonsters || []).map((monster) => {
            const artUrl = partnerArtUrl(monster);
            const isSelected = monster.id === selectedId;
            return (
              <button
                key={monster.id}
                type="button"
                style={rowStyles(isSelected)}
                onClick={() => onSelect(monster)}
              >
                {artUrl ? (
                  <img src={artUrl} alt={monster.name} style={thumbStyles} />
                ) : (
                  <div
                    style={{
                      ...thumbStyles,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '22px',
                    }}
                  >
                    👹
                  </div>
                )}
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                    {monster.name}
                  </div>
                  <div
                    style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)' }}
                  >
                    {monster.species}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </CardSection>
    </Card>
  );
}

export default MonsterChatPicker;
