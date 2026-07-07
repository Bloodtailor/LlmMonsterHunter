// creationSteps.js - the character development wizard's step definitions
// One entry per creation field, in order. LLM-backed steps get their
// options from the generate_player_options workflow; the role step is a
// static code list (the LLM never picks numbers-adjacent things).
// Field names are a CONTRACT with backend/game/player/options.py.

export const CREATION_STEPS = [
  {
    field: 'kind',
    title: 'What are you?',
    subtitle:
      'Anything that walks, drifts, or ticks. A plain human dreamer - or something stranger.',
    placeholder: 'e.g. Human - a stubborn baker who left the ovens behind',
    optionsFromLLM: true,
  },
  {
    field: 'name',
    title: 'What do they call you?',
    subtitle: 'The name your companions will speak around the campfire.',
    placeholder: 'e.g. Marla',
    optionsFromLLM: true,
  },
  {
    field: 'background',
    title: 'Where do you come from?',
    subtitle: 'The life you are walking away from.',
    placeholder: 'e.g. Ran the last bakery on the Low Road until the dream came back.',
    optionsFromLLM: true,
  },
  {
    field: 'personality',
    title: 'How do you carry yourself?',
    subtitle: 'Temperament, manner, edge - the you that others meet.',
    placeholder: 'e.g. Stubborn, warm, allergic to nonsense.',
    optionsFromLLM: true,
  },
  {
    field: 'wish',
    title: 'What is your wish?',
    subtitle:
      'Somewhere below sleeps a power that grants any wish. This one is yours - it will shape your whole story.',
    placeholder: 'e.g. To taste the bread my grandmother baked, once more.',
    optionsFromLLM: true,
  },
  {
    field: 'role',
    title: 'How do you fight?',
    subtitle: 'Your place when the party stands its ground.',
    placeholder: 'e.g. support',
    optionsFromLLM: false,
    staticOptions: [
      'tank - you stand in front and take the hits',
      'striker - you hit hardest, and first',
      'skirmisher - fast, slippery, everywhere at once',
      'support - you keep everyone standing',
      'controller - you bend the field: slow, blind, bind',
      'trickster - you win by cheating fair',
    ],
  },
  {
    field: 'appearance',
    title: 'What do you look like?',
    subtitle: 'Written like an artist’s brief - these exact words become your portrait prompt.',
    placeholder: 'e.g. A square-shouldered woman with burn-scarred forearms and a wooden peel.',
    optionsFromLLM: true,
  },
];

// A static role option carries its explanation after the dash; only the
// word before it is the actual choice sent to the backend
export function roleWordFromOption(optionText) {
  return String(optionText).split(' - ')[0].trim();
}

// How the finalize workflow's step names read on screen (step names are
// a contract with backend/game/player/registered_workflows.py)
export const FORGE_STEP_LABELS = {
  validate_context: 'Reading your answers...',
  building_identity: 'Placing you in the world...',
  shaping_persona: 'Learning who you are...',
  writing_story: 'Writing your story...',
  adding_first_ability: 'Discovering your first talent...',
  adding_second_ability: 'Discovering your second talent...',
};
