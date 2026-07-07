// Monster Evolution Screen - The Evolution Altar at home base
// Home-base only: the backend tracks the REAL run state, so this screen
// checks first and offers the way home instead of letting the ceremony
// fail. Pick a companion on the left, evolve on the right. Evolution is
// the big, earned leap: same monster forever (memories, chat, abilities,
// party place all survive) - remade by everything it has lived, with an
// optional whisper of guidance from you.

import React, { useCallback, useEffect, useState } from 'react';
import { Card, CardSection, Button, Alert, LoadingSpinner } from '../../shared/ui/index.js';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';
import { useParty } from '../../app/contexts/PartyContext/index.js';
import { MonsterChatPicker } from '../../components/chat/index.js';
import { EvolutionCeremonyPanel } from '../../components/evolution/index.js';
import { getDungeonState, abandonRun } from '../../api/services/dungeon.js';

function MonsterEvolutionScreen() {
  const { navigateToGameScreen } = useNavigation();
  const { followingMonsters } = useParty();
  const [selectedMonster, setSelectedMonster] = useState(null);

  // Is the party REALLY home? (backend truth, not frontend navigation)
  const [runCheck, setRunCheck] = useState({ loading: true, inDungeon: false, location: null });
  const [isCallingHome, setIsCallingHome] = useState(false);
  const [runError, setRunError] = useState(null);

  const checkRunState = useCallback(async () => {
    try {
      const state = await getDungeonState();
      setRunCheck({
        loading: false,
        inDungeon: !!state.inDungeon,
        location: state.currentLocation?.name || null,
      });
    } catch (checkError) {
      // If the check itself fails, let the altar try - the backend
      // still enforces the rule when the ceremony is requested
      setRunCheck({ loading: false, inDungeon: false, location: null });
    }
  }, []);

  useEffect(() => {
    checkRunState();
  }, [checkRunState]);

  const handleCallPartyHome = async () => {
    setIsCallingHome(true);
    setRunError(null);
    try {
      await abandonRun();
      await checkRunState();
    } catch (abandonError) {
      setRunError(abandonError?.message || 'Could not call the party home');
    } finally {
      setIsCallingHome(false);
    }
  };

  // The ceremony panel needs the LIVE object - PartyContext patches the
  // following list in place as the ceremony's SSE events land, so the
  // card on the altar transforms in real time
  const liveMonster = selectedMonster
    ? (followingMonsters || []).find((monster) => monster.id === selectedMonster.id) ||
      selectedMonster
    : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <Card size="xl" background="light">
        <CardSection type="header" size="xl" title="⬆️ Evolution Altar" alignment="center">
          <p>
            Everything a companion has lived - every battle, wish, and word - gathers here.
            Evolution makes it more of what it already is.
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

      {/* The party is still down there - offer the way home */}
      {runCheck.loading && (
        <Card size="lg" background="light">
          <CardSection type="content" alignment="center">
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                justifyContent: 'center',
                color: 'var(--color-text-muted)',
              }}
            >
              <LoadingSpinner size="sm" type="spin" />
              Checking on the party...
            </div>
          </CardSection>
        </Card>
      )}

      {!runCheck.loading && runCheck.inDungeon && (
        <Card size="lg" background="light">
          <CardSection
            type="header"
            size="md"
            title="⛰️ Your party is still in the dungeon"
            alignment="center"
          />
          <CardSection type="content" alignment="center">
            <p
              style={{
                color: 'var(--color-text-secondary)',
                maxWidth: '560px',
                margin: '0 auto 12px',
              }}
            >
              {runCheck.location ? `They were last seen at ${runCheck.location}. ` : ''}
              Evolutions happen at home base. Return to the dungeon and finish the run - or call
              everyone home now, which abandons the run where it stands.
            </p>
            <div
              style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}
            >
              <Button
                size="md"
                icon="🏰"
                variant="primary"
                onClick={() => navigateToGameScreen('dungeon-doors')}
              >
                Return to the Dungeon
              </Button>
              <Button
                size="md"
                icon="🏠"
                variant="secondary"
                disabled={isCallingHome}
                onClick={handleCallPartyHome}
              >
                {isCallingHome ? 'Calling them home...' : 'Call the Party Home (abandon run)'}
              </Button>
            </div>
            {runError && (
              <div style={{ marginTop: '12px' }}>
                <Alert type="error" size="md">
                  {runError}
                </Alert>
              </div>
            )}
          </CardSection>
        </Card>
      )}

      {!runCheck.loading && !runCheck.inDungeon && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(240px, 320px) 1fr',
            gap: '24px',
            alignItems: 'start',
          }}
        >
          <MonsterChatPicker
            selectedId={selectedMonster?.id || null}
            onSelect={setSelectedMonster}
            title="🐾 Choose who evolves"
            emptyTitle="No one to evolve yet"
            emptyDescription="Monsters that join you in the dungeon will gather here, ready for the altar."
          />
          <EvolutionCeremonyPanel monster={liveMonster} />
        </div>
      )}
    </div>
  );
}

export default MonsterEvolutionScreen;
