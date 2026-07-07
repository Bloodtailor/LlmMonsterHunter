// DungeonContextPanel - Developer X-ray for LLM context (left-side panel)
// Mirror of the StreamingDisplay pattern: fixed position, clickable header,
// minimize toggle. Shows the dungeon log, battle log, and every context
// block EXACTLY as the dungeon/battle prompts receive them (same backend
// builder functions), including hidden path info. Dev tool - spoilers ahead.

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Badge, Button, Card, CardSection } from '../../shared/ui/index.js';
import { useEventSubscription } from '../../api/events/useEventSubscription.js';
import { getDungeonDebugContext } from '../../api/services/dungeon.js';
import './debugPanel.css';

/**
 * One context block: a titled section rendering the exact prompt text
 */
function ContextBlock({ title, text, note }) {
  if (!text) return null;
  return (
    <CardSection size="sm" title={title}>
      {note && <div className="debug-panel-note">{note}</div>}
      <pre className="debug-context-block">{text}</pre>
    </CardSection>
  );
}

function DungeonContextPanel() {
  // Start minimized - this is a monitoring tool, not the main show
  const [isMinimized, setIsMinimized] = useState(true);
  const [context, setContext] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  // One fetch at a time - workflow events can burst
  const isFetchingRef = useRef(false);
  const isMinimizedRef = useRef(isMinimized);
  isMinimizedRef.current = isMinimized;

  const refresh = useCallback(async () => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;
    try {
      const data = await getDungeonDebugContext();
      if (data.success) {
        setContext(data);
        setLastRefreshed(new Date());
      }
    } catch (error) {
      // Dev tool - stale data is fine, never crash the game over it
      console.warn('Debug context refresh failed:', error);
    } finally {
      isFetchingRef.current = false;
    }
  }, []);

  // Fresh data when the panel opens
  useEffect(() => {
    if (!isMinimized) refresh();
  }, [isMinimized, refresh]);

  // Keep live while open: every finished workflow and every resolved
  // battle turn changes the context the next prompt will receive
  useEventSubscription('workflowCompleted', () => {
    if (!isMinimizedRef.current) refresh();
  });
  useEventSubscription('workflowUpdate', (eventData) => {
    if (!isMinimizedRef.current && eventData?.step === 'action_resolved') refresh();
  });

  const inDungeon = context?.inDungeon;
  const inBattle = context?.battle?.in_battle;
  const dungeonLog = context?.dungeonLog;
  const battle = context?.battle;
  const encounter = context?.encounter;
  const party = context?.party;

  return (
    <div className={`debug-panel ${isMinimized ? 'debug-panel-minimized' : ''}`}>
      {/* Header - always visible, click to toggle */}
      <div className="debug-panel-header" onClick={() => setIsMinimized(!isMinimized)}>
        <div className="debug-panel-status">
          <Badge variant={inBattle ? 'error' : inDungeon ? 'success' : 'info'}>
            {inBattle ? '⚔️ Battle' : inDungeon ? '🧭 Dungeon' : '🔍 Context'}
          </Badge>
          {!isMinimized && lastRefreshed && (
            <span className="debug-panel-note">{lastRefreshed.toLocaleTimeString()}</span>
          )}
        </div>

        <div style={{ display: 'flex', gap: '4px' }}>
          {!isMinimized && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                refresh();
              }}
            >
              🔄
            </Button>
          )}
          <Button size="sm" variant="ghost">
            {isMinimized ? '▶️' : '🔼'}
          </Button>
        </div>
      </div>

      {/* Main content - everything the LLM prompts are built from */}
      {!isMinimized && (
        <Card>
          <div className="debug-panel-scroll">
            {!inDungeon && (
              <CardSection size="sm" title="Not in a dungeon">
                <div className="debug-panel-note">
                  Enter a dungeon to see the context the LLM receives.
                </div>
              </CardSection>
            )}

            {inDungeon && (
              <>
                {/* Where the party is */}
                {context?.currentLocation && (
                  <ContextBlock
                    title="📍 Current Location"
                    text={`${context.currentLocation.name}\n${context.currentLocation.description || ''}`}
                  />
                )}

                {/* The rolling story - injected into every dungeon prompt */}
                <ContextBlock
                  title={`📜 Dungeon Log (${dungeonLog?.entries?.length || 0} entries stored)`}
                  note="Clamped text below is exactly what prompts receive"
                  text={dungeonLog?.clamped_text}
                />

                {/* The party as prompts describe it */}
                <ContextBlock
                  title="🛡️ Party Details (as sent to LLM)"
                  text={party?.details_text}
                />

                {/* The active encounter's blocks */}
                {encounter?.event && (
                  <>
                    <CardSection size="sm" title={`🎭 Encounter: ${encounter.event}`}>
                      <div className="debug-panel-note">
                        {encounter.monsters_present != null &&
                          `monsters_present: ${encounter.monsters_present} · `}
                        {encounter.camped != null && `camped: ${encounter.camped} · `}
                        monster_ids: {JSON.stringify(encounter.monster_ids)}
                      </div>
                    </CardSection>
                    <ContextBlock
                      title="👹 Encounter Monster Details (as sent to LLM)"
                      text={encounter.monster_details_text}
                    />
                    <ContextBlock
                      title="💬 Dialogue History (as sent to LLM)"
                      text={encounter.dialogue_clamped_text}
                    />
                  </>
                )}

                {/* Battle context - what the referee and turn director see */}
                {inBattle && (
                  <>
                    <CardSection
                      size="sm"
                      title={`⚔️ Battle (phase: ${battle.phase}, turn ${battle.turn_count})`}
                    />
                    <ContextBlock
                      title="Battle Situation (as sent to LLM)"
                      text={battle.situation_text}
                    />
                    <ContextBlock
                      title="Turn Director View (speed + waiting)"
                      text={battle.combatant_summary_text}
                    />
                    <ContextBlock
                      title="Turn History (as sent to LLM)"
                      text={battle.turn_history_text}
                    />
                    <ContextBlock
                      title="Battle Log (as sent to LLM)"
                      text={battle.recent_log_text}
                    />
                  </>
                )}

                {/* The hidden truth behind each path - dev X-ray */}
                {context?.pathsFull && Object.keys(context.pathsFull).length > 0 && (
                  <ContextBlock
                    title="🚪 Paths (WITH hidden events + destinations)"
                    note="Spoilers - the player never sees this"
                    text={JSON.stringify(context.pathsFull, null, 2)}
                  />
                )}
              </>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}

export default DungeonContextPanel;
