// ExpeditionNoticeBoard.js - The entrance's expedition picker
// Requests the notice board on arrival, shows the 2-3 posted expeditions
// (title + pitch + danger word), and enters the dungeon with the chosen
// notice - its theme and danger shape the whole run. Hides itself once
// the party sets out (entry text starts streaming).

import React, { useEffect, useRef, useState } from 'react';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';
import { Badge, Button, Card, CardSection, LoadingContainer } from '../../../shared/ui/index.js';

// The danger word decides the badge color - calm invites, perilous warns
const DANGER_BADGE_VARIANTS = {
  calm: 'success',
  risky: 'warning',
  perilous: 'error',
};

function ExpeditionNoticeBoard() {
  const { notices, isGeneratingNotices, entryText, currentLocation, requestNotices, enterDungeon } =
    useDungeon();

  // Which notice the player answered (hides the board while entry queues)
  const [chosenNoticeId, setChosenNoticeId] = useState(null);

  // Ask the board for notices once on arrival (unless a run is already
  // underway - e.g. returning to this screen mid-entry)
  const hasRequestedRef = useRef(false);
  useEffect(() => {
    if (!hasRequestedRef.current && !notices && !isGeneratingNotices && !currentLocation) {
      hasRequestedRef.current = true;
      requestNotices();
    }
  }, [notices, isGeneratingNotices, currentLocation, requestNotices]);

  const setOut = (noticeId) => {
    setChosenNoticeId(noticeId);
    enterDungeon(noticeId);
  };

  // The party has set out - the board's job is done
  if (chosenNoticeId || entryText || currentLocation) {
    return null;
  }

  if (isGeneratingNotices || !notices) {
    return (
      <Card size="xl" background="dark">
        <CardSection type="content" alignment="center" padding="lg">
          <LoadingContainer isLoading={true} loadingText="Posting today's expedition notices..." />
        </CardSection>
      </Card>
    );
  }

  return (
    <Card size="xl" background="dark">
      <CardSection type="header" size="lg" title="📜 Expedition Notices" alignment="center">
        <p>Three postings hang on the board. Choose the expedition your party answers.</p>
      </CardSection>
      <CardSection type="content" padding="md">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {notices.map((notice) => (
            <Card key={notice.id} size="lg" background="light">
              <CardSection type="content" padding="md">
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '8px',
                  }}
                >
                  <strong style={{ fontSize: '1.1em' }}>{notice.title}</strong>
                  <Badge variant={DANGER_BADGE_VARIANTS[notice.danger] || 'secondary'} size="md">
                    {notice.danger}
                  </Badge>
                </div>
                <p style={{ margin: '0 0 12px 0' }}>{notice.pitch}</p>
                <Button variant="primary" size="md" onClick={() => setOut(notice.id)}>
                  Answer This Notice
                </Button>
              </CardSection>
            </Card>
          ))}
        </div>
      </CardSection>
    </Card>
  );
}

export default ExpeditionNoticeBoard;
