// CharacterCreationScreen.js - the character development wizard
// New Game (after the wipe) lands here. Three phases: STEPS (one field
// at a time - options + free text), FORGE (the finalize workflow's live
// card reveal), PORTRAIT (paint candidates / upload / skip). Ends at
// the guided first run. A world that already has a finished character
// skips straight through - New Game is the only door back in.

import React, { useEffect, useRef, useState } from 'react';
import { Card, CardSection } from '../../shared/ui/index.js';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';
import * as playerApi from '../../api/services/player.js';
import CreationStep from '../../components/player/CreationStep.js';
import CharacterForge from '../../components/player/CharacterForge.js';
import PortraitStage from '../../components/player/PortraitStage.js';
import { CREATION_STEPS, roleWordFromOption } from '../../components/player/creationSteps.js';

function CharacterCreationScreen() {
  const { navigateToGameScreen } = useNavigation();

  const [phase, setPhase] = useState('steps'); // steps -> forge -> portrait
  const [stepIndex, setStepIndex] = useState(0);
  const [choices, setChoices] = useState({});
  const [draft, setDraft] = useState('');
  const [player, setPlayer] = useState(null);

  // A finished character means creation already happened - go to the
  // opening (New Game wipes the world BEFORE this screen, so a living
  // character here is a back-button or refresh, not a fresh start)
  const guardedRef = useRef(false);
  useEffect(() => {
    if (guardedRef.current) return;
    guardedRef.current = true;
    playerApi.getPlayer().then(({ player: existing }) => {
      if (existing && existing.generationStage === 'complete') {
        navigateToGameScreen('first-run-opening');
      }
    });
  }, [navigateToGameScreen]);

  const step = CREATION_STEPS[stepIndex];

  const saveDraftAndAdvance = () => {
    // The role step stores only the role WORD; its explanation is UI
    const value = step.field === 'role' ? roleWordFromOption(draft) : draft.trim();
    const nextChoices = { ...choices, [step.field]: value };
    setChoices(nextChoices);

    if (stepIndex + 1 < CREATION_STEPS.length) {
      setStepIndex(stepIndex + 1);
      setDraft(nextChoices[CREATION_STEPS[stepIndex + 1].field] || '');
    } else {
      setPhase('forge');
    }
  };

  const goBack = () => {
    if (stepIndex === 0) return;
    const previous = CREATION_STEPS[stepIndex - 1];
    setChoices({ ...choices, [step.field]: draft.trim() });
    setStepIndex(stepIndex - 1);
    setDraft(choices[previous.field] || '');
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        maxWidth: '760px',
        margin: '32px auto 0',
      }}
    >
      <Card size="xl" background="dark">
        <CardSection type="header" size="xl" title="✍️ Who walks into the dark?" alignment="center">
          <p style={{ fontStyle: 'italic', color: 'var(--color-text-secondary)', margin: 0 }}>
            The power below grants any wish - but first, there has to be a you.
          </p>
        </CardSection>
      </Card>

      {phase === 'steps' && (
        <CreationStep
          key={step.field}
          step={step}
          choices={choices}
          value={draft}
          onChange={setDraft}
          onNext={saveDraftAndAdvance}
          onBack={goBack}
          canBack={stepIndex > 0}
          stepLabel={`Step ${stepIndex + 1} of ${CREATION_STEPS.length}`}
        />
      )}

      {phase === 'forge' && (
        <CharacterForge
          choices={choices}
          onForged={(forged) => {
            setPlayer(forged);
            setPhase('portrait');
          }}
        />
      )}

      {phase === 'portrait' && (
        <PortraitStage player={player} onDone={() => navigateToGameScreen('first-run-opening')} />
      )}
    </div>
  );
}

export default CharacterCreationScreen;
