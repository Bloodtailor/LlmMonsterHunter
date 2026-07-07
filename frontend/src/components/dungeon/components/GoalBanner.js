// GoalBanner.js - The run's goal, always in view while exploring
// Shows the goal text, a checkmark once the goal referee marks it
// complete, and the latest progress note. Renders nothing when the run
// has no goal (ordinary expeditions and older saves).

import React from 'react';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';
import { Badge, Card, CardSection } from '../../../shared/ui/index.js';

function GoalBanner() {
  const { goal } = useDungeon();

  if (!goal || !goal.text) return null;

  const isComplete = goal.status === 'complete';
  const latestNote =
    goal.progress_notes && goal.progress_notes.length > 0
      ? goal.progress_notes[goal.progress_notes.length - 1]
      : null;

  return (
    <Card size="xl" background="dark">
      <CardSection type="content" padding="sm">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <Badge variant={isComplete ? 'success' : 'info'} size="md">
            {isComplete ? '✓ Goal fulfilled' : '🎯 Goal'}
          </Badge>
          <span
            style={{
              color: 'var(--color-text-primary)',
              fontStyle: 'italic',
              textDecoration: isComplete ? 'line-through' : 'none',
            }}
          >
            {goal.text}
          </span>
        </div>
        {!isComplete && latestNote && (
          <p
            style={{
              margin: '8px 0 0 0',
              color: 'var(--color-text-muted)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            Latest progress: {latestNote}
          </p>
        )}
      </CardSection>
    </Card>
  );
}

export default GoalBanner;
