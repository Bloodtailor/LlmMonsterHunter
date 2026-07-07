// Monster Chat Screen - Sit down with the monsters that follow you
// Home-base only (the backend refuses chats mid-run). Pick a companion
// on the left, talk on the right. Conversations are persistent - one
// thread per monster for the whole save - and the moments that matter
// become permanent memories that shape how the monster fights, grows,
// and meets others.

import React, { useState } from 'react';
import { Card, CardSection, Button } from '../../shared/ui/index.js';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';
import { MonsterChatPicker, MonsterChatPanel } from '../../components/chat/index.js';

function MonsterChatScreen() {
  const { navigateToGameScreen } = useNavigation();
  const [selectedMonster, setSelectedMonster] = useState(null);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <Card size="xl" background="light">
        <CardSection type="header" size="xl" title="🔥 Campfire Chat" alignment="center">
          <p>
            Time between dungeon runs belongs to your companions. What you talk
            about stays with them.
          </p>
        </CardSection>
        <CardSection type="content" alignment="center">
          <Button
            size="md"
            icon="🏠"
            variant="secondary"
            onClick={() => navigateToGameScreen('homebase')}
          >
            Back to Home Base
          </Button>
        </CardSection>
      </Card>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(240px, 320px) 1fr',
          gap: '24px',
          alignItems: 'start'
        }}
      >
        <MonsterChatPicker
          selectedId={selectedMonster?.id || null}
          onSelect={setSelectedMonster}
        />
        <MonsterChatPanel monster={selectedMonster} />
      </div>
    </div>
  );
}

export default MonsterChatScreen;
