// useMonsterEvolution.js - The whole evolution ceremony state machine for ONE monster
// begin() snapshots the before-form and queues the evolve_monster workflow;
// the transform lands via monster.evolved (identity/stats/rarity flipped in
// place), the ceremony text streams (workflow step emit_generation_id ->
// evolution_text_generation_id), later stages patch the live card through
// PartyContext, and workflow.completed closes the ceremony with the full
// result (narrative, signature ability, reworded abilities, art flag).

import { useCallback, useEffect, useRef, useState } from 'react';
import { evolveMonster as requestEvolution } from '../../../api/services/monster.js';
import { useEventSubscription } from '../../../api/events/useEventSubscription.js';
import { useStreamedGeneration } from '../../../api/events/useStreamedGeneration.js';

// The workflow's step names as ceremony language
export const EVOLUTION_STEP_LABELS = {
  validate_context: 'Preparing the altar',
  designing_form: 'Listening to its history',
  applying_form: 'The change takes hold',
  form_applied: 'The change takes hold',
  queue_narration: 'Finding the words',
  emit_generation_id: 'Finding the words',
  await_narration: 'The story tells itself',
  shifting_persona: 'Its inner life settles',
  rewriting_story: 'A new chapter is written',
  evolving_abilities: 'Its powers evolve',
  adding_signature_ability: 'A signature awakens',
  recording_memory: 'It will remember this',
  regenerating_art: 'A new face emerges',
};

/**
 * Hook managing one monster's evolution ceremony
 * @param {object|null} monster - The selected companion (live object from PartyContext)
 * @returns {object} Ceremony state and actions
 */
export function useMonsterEvolution(monster) {
  const [phase, setPhase] = useState('idle'); // idle | evolving | complete | failed
  const [currentStep, setCurrentStep] = useState(null);
  const [narration, setNarration] = useState('');
  const [beforeSnapshot, setBeforeSnapshot] = useState(null);
  const [evolution, setEvolution] = useState(null); // the lineage record, from monster.evolved
  const [result, setResult] = useState(null); // workflow.completed payload
  const [artRevealed, setArtRevealed] = useState(false);
  const [error, setError] = useState(null);

  // The companion the in-flight events belong to (avoids stale closures)
  const monsterIdRef = useRef(monster?.id || null);
  monsterIdRef.current = monster?.id || null;
  const phaseRef = useRef(phase);
  phaseRef.current = phase;
  const workflowIdRef = useRef(null);

  // A new companion on the altar means a fresh ceremony
  useEffect(() => {
    setPhase('idle');
    setCurrentStep(null);
    setNarration('');
    setBeforeSnapshot(null);
    setEvolution(null);
    setResult(null);
    setArtRevealed(false);
    setError(null);
    workflowIdRef.current = null;
  }, [monster?.id]);

  // ===== BEGIN =====

  const begin = useCallback(
    async (guidance) => {
      if (!monsterIdRef.current || phaseRef.current === 'evolving') return;

      setError(null);
      setCurrentStep(null);
      setNarration('');
      setEvolution(null);
      setResult(null);
      setArtRevealed(false);
      // The before-form, frozen at the moment the player commits
      setBeforeSnapshot(JSON.parse(JSON.stringify(monster)));
      setPhase('evolving');

      try {
        const response = await requestEvolution(monsterIdRef.current, guidance);
        workflowIdRef.current = response.workflowId;
      } catch (beginError) {
        // The backend refused (mid-run, not following...) - nothing happened
        setPhase('failed');
        setBeforeSnapshot(null);
        setError(beginError?.message || 'The altar stays dark - evolution could not begin');
      }
    },
    [monster],
  );

  const reset = useCallback(() => {
    setPhase('idle');
    setCurrentStep(null);
    setNarration('');
    setBeforeSnapshot(null);
    setEvolution(null);
    setResult(null);
    setArtRevealed(false);
    setError(null);
    workflowIdRef.current = null;
  }, []);

  // ===== THE CEREMONY, ARRIVING OVER SSE =====

  useEventSubscription('workflowUpdate', ({ workflowId, workflowType, step }) => {
    if (workflowType !== 'evolve_monster') return;
    if (workflowIdRef.current && workflowId !== workflowIdRef.current) return;
    setCurrentStep(step);
  });

  useStreamedGeneration('evolution_text_generation_id', {
    onText: (partialText) => setNarration(partialText),
  });

  // The transform moment - the lineage record carries the old form
  useEventSubscription('monsterEvolved', ({ monster: evolvedMonster, evolution: record }) => {
    if (!record || evolvedMonster?.id !== monsterIdRef.current) return;
    setEvolution(record);
  });

  // The regenerated card art landed (PartyContext repoints the card image;
  // this flag lets the ceremony celebrate the reveal)
  useEventSubscription('monsterArtReady', ({ monsterId }) => {
    if (monsterId !== monsterIdRef.current) return;
    if (phaseRef.current === 'evolving' || phaseRef.current === 'complete') {
      setArtRevealed(true);
    }
  });

  useEventSubscription(
    'workflowCompleted',
    ({ workflowItem, workflowId, result: workflowResult }) => {
      if (workflowItem?.workflowType !== 'evolve_monster') return;
      if (workflowIdRef.current && workflowId !== workflowIdRef.current) return;
      if (!workflowResult || workflowResult.monster_id !== monsterIdRef.current) return;
      setResult(workflowResult);
      setNarration((prev) => workflowResult.narrative || prev);
      setPhase('complete');
    },
  );

  useEventSubscription('workflowFailed', ({ workflowItem, workflowId, error: failure }) => {
    if (workflowItem?.workflowType !== 'evolve_monster') return;
    if (workflowIdRef.current && workflowId !== workflowIdRef.current) return;
    const detail = typeof failure === 'string' ? failure : failure?.error;
    setPhase('failed');
    setError(detail || 'The evolution faltered - your companion is unchanged');
  });

  return {
    phase,
    currentStep,
    narration,
    beforeSnapshot,
    evolution,
    result,
    artRevealed,
    error,
    begin,
    reset,
  };
}
