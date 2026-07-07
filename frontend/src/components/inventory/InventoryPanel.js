// InventoryPanel.js - The party's possessions: Items and CoCaTok keepsakes
// Two paginated tabs. Items show what the referee will read when they are
// used; CoCaToks render on the spinning card component as view-only
// keepsakes (their explosion ceremony already happened at pickup).

import React, { useState, useEffect, useCallback } from 'react';
import { usePagination } from '../../shared/ui/Pagination/usePagination.js';
import FullPagination, {
  PAGINATION_LAYOUTS,
} from '../../shared/ui/Pagination/PaginationPresets.js';
import { useInventoryCollection } from '../../app/hooks/useInventory.js';
import CoCaTok from '../../shared/ui/CoCaTok/CoCaTok.js';
import { Alert, Badge, Button, EmptyState, LoadingSpinner } from '../../shared/ui/index.js';

const TABS = [
  { key: 'items', label: '🎒 Items' },
  { key: 'cocatoks', label: '🏆 CoCaToks' },
];

function InventoryPanel({ pageSize = 8 }) {
  const [tab, setTab] = useState('items');

  const { entries, total, isLoading, isError, error, load } = useInventoryCollection(tab);
  const pagination = usePagination({ limit: pageSize, total });

  const loadPage = useCallback(() => {
    load({ limit: pageSize, offset: pagination.currentOffset });
  }, [load, pageSize, pagination.currentOffset]);

  useEffect(() => {
    loadPage();
  }, [loadPage]);

  const handleTabChange = (nextTab) => {
    if (nextTab === tab) return;
    setTab(nextTab);
    pagination.firstPage();
  };

  return (
    <div>
      {/* Tab toggle */}
      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginBottom: '16px' }}>
        {TABS.map(({ key, label }) => (
          <Button
            key={key}
            size="sm"
            variant={tab === key ? 'primary' : 'secondary'}
            onClick={() => handleTabChange(key)}
          >
            {label}
          </Button>
        ))}
      </div>

      {isError && (
        <Alert type="error" title="Inventory Error">
          {error?.message || 'Failed to load the inventory'}
        </Alert>
      )}

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <LoadingSpinner size="section" type="spin" />
        </div>
      ) : entries.length === 0 ? (
        <EmptyState
          icon={tab === 'items' ? '🎒' : '🏆'}
          title={tab === 'items' ? 'No Items Yet' : 'No CoCaToks Yet'}
          message={
            tab === 'items'
              ? 'Treasures wait on hidden dungeon paths, and grateful monsters give gifts.'
              : 'Win battles to mint unique keepsakes commemorating your victories.'
          }
          size="md"
        />
      ) : tab === 'items' ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {entries.map((item) => (
            <div
              key={item.id}
              style={{
                display: 'flex',
                gap: '12px',
                alignItems: 'flex-start',
                padding: '12px',
                borderRadius: 'var(--radius-sm, 8px)',
                background: 'var(--color-surface-secondary, rgba(0,0,0,0.15))',
              }}
            >
              <span style={{ fontSize: '1.8rem', lineHeight: 1 }}>{item.emoji}</span>
              <div style={{ flex: 1 }}>
                <div
                  style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}
                >
                  <span style={{ fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                    {item.name}
                  </span>
                  <Badge variant="info" size="sm" pill>
                    {item.usesRemaining} use{item.usesRemaining === 1 ? '' : 's'} left
                  </Badge>
                </div>
                <p
                  style={{
                    margin: '4px 0 0',
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-text-secondary)',
                  }}
                >
                  {item.description}
                </p>
                {item.sourceNote && (
                  <p
                    style={{
                      margin: '4px 0 0',
                      fontSize: 'var(--font-size-xs)',
                      fontStyle: 'italic',
                      color: 'var(--color-text-muted)',
                    }}
                  >
                    {item.sourceNote}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {entries.map((cocatok) => (
            <div
              key={cocatok.id}
              style={{
                display: 'flex',
                gap: '16px',
                alignItems: 'center',
                padding: '12px',
                borderRadius: 'var(--radius-sm, 8px)',
                background: 'var(--color-surface-secondary, rgba(0,0,0,0.15))',
              }}
            >
              {/* A keepsake: it spins forever, and nothing can destroy it */}
              <CoCaTok color={cocatok.color} emoji={cocatok.emoji} size="sm" disabled={true} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                  {cocatok.emoji} {cocatok.title}
                </div>
                <p
                  style={{
                    margin: '4px 0 0',
                    fontSize: 'var(--font-size-sm)',
                    fontStyle: 'italic',
                    fontFamily: 'var(--font-family-serif)',
                    color: 'var(--color-text-secondary)',
                  }}
                >
                  {cocatok.commemoration}
                </p>
                <p
                  style={{
                    margin: '4px 0 0',
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-text-muted)',
                  }}
                >
                  {cocatok.locationName ? `${cocatok.locationName} — ` : ''}
                  {cocatok.earnedAt ? cocatok.earnedAt.toLocaleDateString() : ''}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > pageSize && (
        <div style={{ marginTop: '16px' }}>
          <FullPagination
            pagination={pagination}
            itemName={tab === 'items' ? 'items' : 'CoCaToks'}
            layout={PAGINATION_LAYOUTS.DEFAULT}
          />
        </div>
      )}
    </div>
  );
}

export default InventoryPanel;
