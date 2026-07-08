// EvolutionLineage.js - The forms a monster has left behind, oldest first
// Reads the lineage records (old art thumbnails stay servable forever -
// evolution never deletes art files) and shows each ceremony's story.

import React, { useEffect, useState } from 'react';
import { Card, CardSection, LoadingSpinner } from '../../shared/ui/index.js';
import { loadMonsterEvolutions, getCardArtUrl } from '../../api/services/monster.js';

/**
 * EvolutionLineage component
 * @param {number|null} monsterId - Whose lineage to show
 * @param {any} refreshToken - Changing this value reloads the lineage
 *   (the ceremony panel passes its phase so completions refresh the list)
 */
function EvolutionLineage({ monsterId, refreshToken }) {
  const [evolutions, setEvolutions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!monsterId) {
      setEvolutions([]);
      return undefined;
    }
    let cancelled = false;
    setLoading(true);
    loadMonsterEvolutions(monsterId)
      .then(({ evolutions: rows }) => {
        if (!cancelled) setEvolutions(rows);
      })
      .catch(() => {
        if (!cancelled) setEvolutions([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [monsterId, refreshToken]);

  // No lineage yet - stay out of the way
  if (!monsterId || (!loading && evolutions.length === 0)) return null;

  return (
    <Card size="lg" background="light">
      <CardSection type="header" size="md" title="📜 Lineage" alignment="center" />
      <CardSection type="content">
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '12px' }}>
            <LoadingSpinner size="sm" type="spin" />
          </div>
        )}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {evolutions.map((evolution) => {
            const artUrl = getCardArtUrl(evolution.oldCardArtPath);
            return (
              <div
                key={evolution.id}
                style={{
                  display: 'flex',
                  gap: '12px',
                  alignItems: 'flex-start',
                  background: 'var(--color-background-medium)',
                  borderRadius: '10px',
                  padding: '10px 12px',
                }}
              >
                {artUrl ? (
                  <img
                    src={artUrl}
                    alt={evolution.oldName}
                    style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '8px',
                      objectFit: 'cover',
                      flexShrink: 0,
                      opacity: 0.8,
                    }}
                  />
                ) : (
                  <div
                    style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '8px',
                      flexShrink: 0,
                      background: 'var(--color-background-dark)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '20px',
                    }}
                  >
                    👹
                  </div>
                )}
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontWeight: 'bold' }}>
                    Stage {evolution.stage}: {evolution.oldName} the {evolution.oldSpecies}
                    <span style={{ color: 'var(--color-text-muted)' }}> → </span>
                    {evolution.newName} the {evolution.newSpecies}
                  </div>
                  <div
                    style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)' }}
                  >
                    {evolution.oldRarity || 'common'} → {evolution.newRarity}
                    {evolution.createdAt ? ` · ${evolution.createdAt.toLocaleDateString()}` : ''}
                    {evolution.guidance ? ` · whispered: "${evolution.guidance}"` : ''}
                  </div>
                  {evolution.narrative && (
                    <div
                      style={{
                        fontSize: 'var(--font-size-sm)',
                        color: 'var(--color-text-secondary)',
                        fontStyle: 'italic',
                        marginTop: '4px',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {evolution.narrative}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardSection>
    </Card>
  );
}

export default EvolutionLineage;
