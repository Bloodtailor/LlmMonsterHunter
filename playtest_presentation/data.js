// The deck. Every number here is measured, and every slide points at the
// file that produced it - the links open the real source in this repo.
const DECK = [
  {
    eyebrow: 'The problem',
    title: 'Development outran playtesting',
    audio: 'audio/01.mp3',
    lede:
      'A game that writes itself cannot be tested by playing it. One expedition costs real minutes and real money, and covers one path out of thousands.',
    body: [
      'Every monster, location and negotiation is written on demand by a language model and refereed by another, with code owning the numbers. That is what makes the game interesting — and what makes a human playtester the slowest part of the project.',
      'This session had one job: make the whole game testable without anyone at the keyboard, and make it re-runnable at every future milestone.',
    ],
    files: [
      { label: 'docs/plans/playtest-suite-expansion.md', href: '../docs/plans/playtest-suite-expansion.md' },
      { label: 'CLAUDE.md', href: '../CLAUDE.md' },
    ],
  },
  {
    eyebrow: 'Where we started',
    title: 'The founding harness',
    audio: 'audio/02.mp3',
    body: [
      'The previous session built the groundwork: a crash driver that walks real workflows with the model stubbed out, a corpus generator that measures writing quality by <strong>counting</strong> rather than asking a model to judge prose it would have written itself, a step CLI so an agent can play one command at a time, and a scorer that checks an agent\'s claims against its own transcript.',
      'It hammered the dungeon loop and left every other system to chance.',
    ],
    metrics: [
      { value: '201', label: 'stubbed runs' },
      { value: '2', label: 'real bugs found' },
      { value: '150', label: 'monster corpus' },
      { value: '$0.41', label: 'for 920 calls' },
    ],
    files: [
      { label: 'docs/plans/playtest-harness.md', href: '../docs/plans/playtest-harness.md' },
      { label: 'playtest_results/REPORT.md', href: '../playtest_results/REPORT.md' },
      { label: 'tools/playtest/crash_driver.py', href: '../tools/playtest/crash_driver.py' },
    ],
  },
  {
    eyebrow: 'The mandate',
    title: 'A suite, not a museum',
    audio: 'audio/03.mp3',
    body: [
      'Decide everything that needs testing and build a test for each. Try several methods per surface, keep what works, delete what does not. Make every part one-command runnable at any future milestone.',
      'The locked rules carried over: never touch the development database, never enable image generation, count rather than judge, and treat every claim an AI makes about its own work as a claim until the transcript proves it.',
    ],
    ladder: [
      { text: 'dungeon loop', state: 'hit' },
      { text: 'battle', state: 'hit' },
      { text: 'campfire chat', state: 'hit' },
      { text: 'evolution', state: 'hit' },
      { text: 'cross-run memory', state: 'hit' },
      { text: 'chronicles', state: 'hit' },
      { text: 'adversarial input', state: 'hit' },
      { text: 'cost & latency', state: 'hit' },
      { text: 'the real UI', state: 'hit' },
    ],
    files: [
      { label: 'docs/plans/playtest-suite-expansion.md', href: '../docs/plans/playtest-suite-expansion.md' },
    ],
  },
  {
    eyebrow: 'Px-M1 · fixes',
    title: 'Two bugs, closed properly',
    audio: 'audio/04.mp3',
    body: [
      '<strong>The sneak collision.</strong> A failed sneak returned a payload whose <code>success</code> flag overwrote the envelope\'s own flag, so a completely normal outcome — the party gets noticed — was recorded as a failed workflow and surfaced as an error instead of a battle. One renamed key, one frontend line.',
      '<strong>The exit with no fallback.</strong> Of everything the game generates, the exit narration was the only text with no deterministic fallback — and it is the first step of the only way out. During a provider outage the party could walk deeper forever but never leave.',
    ],
    bars: [
      { name: 'broken-mode runs able to exit — before', pct: 0, readout: '0 / 14', tone: 'warn' },
      { name: 'broken-mode runs able to exit — after', pct: 67, readout: '4 / 6', tone: 'good' },
      { name: 'invariant violations, 20 happy runs', pct: 0, readout: '0', tone: 'good' },
    ],
    files: [
      { label: 'backend/game/dungeon/handlers/stealth.py', href: '../backend/game/dungeon/handlers/stealth.py' },
      { label: 'backend/game/dungeon/generator.py', href: '../backend/game/dungeon/generator.py' },
      { label: 'useDungeonEvents.js', href: '../frontend/src/app/contexts/DungeonContext/hooks/useDungeonEvents.js' },
    ],
  },
  {
    eyebrow: 'The invention',
    title: 'A referee you can script',
    audio: 'audio/05.mp3',
    lede:
      'The existing stub answered at random — perfect for finding crashes, useless for asking a specific question.',
    body: [
      'The scripted stub pins any single answer the referee gives — <em>this sneak fails, these enemies yield, this monster joins</em> — while everything else stays random and free. A companion pins the game\'s own dice, so a test can say "every path from here holds a battle".',
      'Together they turn the game from something you observe into something you interrogate. No game code changed: the harness stays a consumer of the two seams that already existed.',
    ],
    files: [
      { label: 'tools/playtest/scripted_stub.py', href: '../tools/playtest/scripted_stub.py' },
      { label: 'tools/playtest/gauntlet_rig.py', href: '../tools/playtest/gauntlet_rig.py' },
      { label: 'tools/playtest/stub_llm.py', href: '../tools/playtest/stub_llm.py' },
    ],
  },
  {
    eyebrow: 'Px-M1 · battle',
    title: 'The battle gauntlet',
    audio: 'audio/06.mp3',
    body: [
      'Six scenarios, each an assertion about a promise the design makes in prose and had never checked: the softlock valve caps enemy streaks, the fairness guardrail lets nobody starve, all five negotiation decisions do what their word says, defeat forfeits the run\'s recruits while leaving their memories intact, costs walk the resource ladder and clamp, and a wary ally refuses orders until its affinity reaches familiar.',
    ],
    ladder: [
      { text: 'brimming', state: 'hit' },
      { text: 'steady' },
      { text: 'strained' },
      { text: 'drained', state: 'hit' },
      { text: 'spent', state: 'hit' },
      { text: 'past spent', state: 'blocked' },
    ],
    metrics: [
      { value: '7', label: 'scenarios' },
      { value: '49', label: 'checks', tone: 'good' },
      { value: '9s', label: 'wall time' },
      { value: '$0', label: 'cost', tone: 'good' },
    ],
    files: [
      { label: 'tools/playtest/battle_gauntlet.py', href: '../tools/playtest/battle_gauntlet.py' },
      { label: 'backend/game/battle/constants.py', href: '../backend/game/battle/constants.py' },
      { label: 'backend/game/battle/turn/director.py', href: '../backend/game/battle/turn/director.py' },
    ],
  },
  {
    eyebrow: 'Px-M2 · the dungeon',
    title: 'Every path event, on purpose',
    audio: 'audio/07.mp3',
    body: [
      'The crash driver reaches rare events by luck. This suite forces each one: treasure that only becomes real when the party walks out alive, the full six-outcome dialogue tree with the permanent memory each outcome writes, the out-of-battle referee, camp with its one-camp valve, and the exit ceremony.',
      'It also produced the night\'s prettiest finding: a scripted goal completion did not take, because the game deliberately refuses to complete a goal in fewer than three resolved events. Not a bug — a valve, working, and now covered.',
    ],
    metrics: [
      { value: '7', label: 'scenarios' },
      { value: '43', label: 'checks', tone: 'good' },
      { value: '5s', label: 'wall time' },
      { value: '1', label: 'valve documented' },
    ],
    files: [
      { label: 'tools/playtest/dungeon_gauntlet.py', href: '../tools/playtest/dungeon_gauntlet.py' },
      { label: 'backend/game/dungeon/goal.py', href: '../backend/game/dungeon/goal.py' },
      { label: 'backend/game/dungeon/spoils.py', href: '../backend/game/dungeon/spoils.py' },
    ],
  },
  {
    eyebrow: 'Px-M2 · the life',
    title: 'Chat, evolution, and the arc across runs',
    audio: 'audio/08.mp3',
    body: [
      'Three systems live outside the dungeon loop and none had ever been tested headlessly. Chat: four exchanges cross the extraction threshold, housekeeping runs behind the player, memories are written with the message span they came from, and a conversation that produced real memories deepens the bond.',
      'Evolution transforms a monster in place — same identifier, memories and abilities intact, a lineage row recording the step. And the arc that spans runs: a monster that yields in one expedition returns in the next, remembering the yield and naming the place it happened.',
    ],
    metrics: [
      { value: '3', label: 'scenarios' },
      { value: '23', label: 'checks', tone: 'good' },
      { value: 'same id', label: 'after evolution' },
      { value: '2 runs', label: 'memory arc' },
    ],
    files: [
      { label: 'tools/playtest/life_gauntlet.py', href: '../tools/playtest/life_gauntlet.py' },
      { label: 'backend/game/chat/registered_workflows.py', href: '../backend/game/chat/registered_workflows.py' },
      { label: 'backend/game/memory/returning.py', href: '../backend/game/memory/returning.py' },
    ],
  },
  {
    eyebrow: 'Px-M2 · method',
    title: 'Faithfulness, counted not judged',
    audio: 'audio/09.mp3',
    lede:
      'Chat produces the game\'s most dangerous text: memories that persist forever and colour every later conversation.',
    body: [
      'The question is whether an extracted memory is faithful to what was said — and the one thing you must not do is ask a language model to grade another one, for the same reason you never ask it whether its own writing is varied.',
      'So it counts instead: how much of a memory\'s own vocabulary actually appears in the exact stretch of transcript it claims to summarise. The checker was validated by planting one true memory and one fabrication in a real thread and confirming it flags exactly the fabrication.',
    ],
    wall: {
      attacks: ['"the sunfall bridge…"', '"copper bells the toll keeper sang"', '"the flooded orchard road"'],
      barrier: 'overlap score',
      held: ['faithful memory — passes', 'fabricated "moon dragon of Zanzibar" — flagged'],
    },
    files: [
      { label: 'tools/playtest/chat_faithfulness.py', href: '../tools/playtest/chat_faithfulness.py' },
      { label: 'backend/game/chat/manager.py', href: '../backend/game/chat/manager.py' },
    ],
  },
  {
    eyebrow: 'Px-M3 · adversarial',
    title: 'The boundary-pusher',
    audio: 'audio/10.mp3',
    lede:
      'The architecture promises the model picks words and code owns numbers. This tests that promise against a real model.',
    body: [
      'Hostile text goes into every free-text field the game exposes — battle talk, custom actions, dungeon dialogue, ability targets. After each one the probe asserts only the things <strong>code</strong> owns. Prose compliance is not a breach; the numbers are.',
      '<strong>Fifty checks against a real model, zero failures.</strong> The referee occasionally narrated along with an attack — and the state never moved.',
    ],
    wall: {
      attacks: [
        'fake system prompt',
        'forged referee JSON',
        'developer-authority claim',
        '"use impact annihilated"',
        '"the enemies already fled"',
      ],
      barrier: 'code owns the numbers',
      held: [
        'every word stayed on its ladder',
        'no roster rewritten',
        'no unearned victory recorded',
        'every dialogue outcome inside the enum',
      ],
    },
    metrics: [
      { value: '50', label: 'live checks', tone: 'good' },
      { value: '0', label: 'breaches', tone: 'good' },
      { value: '4', label: 'attack surfaces' },
      { value: '~$0.15', label: 'to run' },
    ],
    files: [
      { label: 'tools/playtest/adversarial_probe.py', href: '../tools/playtest/adversarial_probe.py' },
      { label: 'tools/playtest/adversarial_agent_prompt.md', href: '../tools/playtest/adversarial_agent_prompt.md' },
      { label: 'backend/game/battle/manager.py', href: '../backend/game/battle/manager.py' },
    ],
  },
  {
    eyebrow: 'Px-M3 · the bake-off',
    title: 'Who should do the testing',
    audio: 'audio/11.mp3',
    lede:
      'Both models play competently. Only the transcript tells you what actually happened.',
    body: [
      'Haiku never ran <code>new-world</code>: it silently inherited the previous session\'s world and reported its leftovers as the game\'s behaviour — the same failure the founding night saw in stubs, now confirmed with real narration. Its one bug claim was real all the same.',
      'Sonnet completed the loop, walked out alive, and produced three claims: one genuine defect (the stale paths, fixed the same night), one harness artifact, one prompt-quality issue.',
      '<strong>The standard tester is sonnet</strong> for feedback worth acting on, with haiku as a cheap play-monkey behind the objective scorer.',
    ],
    table: {
      columns: ['tester', 'invalid actions', 'followed setup', 'verified findings'],
      rows: [
        ['haiku', '0.0', 'no', '1'],
        ['sonnet', '0.0', 'yes', '3'],
      ],
    },
    files: [
      { label: 'tools/playtest/play.py', href: '../tools/playtest/play.py' },
      { label: 'tools/playtest/score_session.py', href: '../tools/playtest/score_session.py' },
      { label: 'tools/playtest/agent_playtester_prompt.md', href: '../tools/playtest/agent_playtester_prompt.md' },
    ],
  },
  {
    eyebrow: 'Px-M4 · variety',
    title: 'The writing breaks its own rule',
    audio: 'audio/12.mp3',
    lede:
      'Counting found something nobody had quantified: more than half of generated abilities promise mechanics the engine does not implement.',
    body: [
      'The game\'s rule is that power lives in words and code owns every number. The ability generator has been quietly breaking it — durations in turns, damage types, quantified pools. Players read those as promises; the referee never honours them.',
    ],
    bars: [
      { name: 'abilities promising a mechanic', pct: 57, readout: '57%', tone: 'warn' },
      { name: '… naming a number of turns', pct: 33, readout: '33%', tone: 'warn' },
      { name: '… "next N turns"', pct: 20, readout: '20%', tone: 'warn' },
      { name: '… naming a damage type', pct: 20, readout: '20%', tone: 'warn' },
      { name: 'abilities echoing "deepest wish"', pct: 65, readout: '65%', tone: 'warn' },
    ],
    files: [
      { label: 'tools/playtest/analyze_text_corpus.py', href: '../tools/playtest/analyze_text_corpus.py' },
      { label: 'tools/playtest/variety_metrics.py', href: '../tools/playtest/variety_metrics.py' },
      { label: 'backend/ai/llm/prompts/ability_generation.json', href: '../backend/ai/llm/prompts/ability_generation.json' },
    ],
  },
  {
    eyebrow: 'Px-M4 · cost',
    title: 'Reading the ledger nobody read',
    audio: 'audio/13.mp3',
    body: [
      'Every generation the game has ever run wrote a row recording its template, its exact token counts and how long it took. The cost report turns that into two tables: what one player action costs, and which template is the expensive one.',
      'The whole night — every corpus, every probe, every live playtest — cost <strong>$1.51</strong>. But it spent <strong>225 minutes</strong> of generation time, and input tokens outweigh output <strong>eleven to one</strong>: context is the bill, not prose.',
    ],
    bars: [
      { name: 'monster generation', pct: 67, readout: '151 min', tone: 'warn' },
      { name: 'everything else', pct: 33, readout: '74 min' },
    ],
    table: {
      columns: ['template', 'calls', 'tokens', 'avg s'],
      rows: [
        ['action_resolution', '179', '1,064,361', '3.71'],
        ['next_turn', '186', '785,945', '1.57'],
        ['monster_social_self', '246', '317,963', '11.01'],
        ['monster_creative_text', '240', '265,882', '11.65'],
      ],
    },
    files: [
      { label: 'tools/playtest/cost_report.py', href: '../tools/playtest/cost_report.py' },
      { label: 'backend/models/llm_log.py', href: '../backend/models/llm_log.py' },
    ],
  },
  {
    eyebrow: 'Px-M5 · the real UI',
    title: 'Through the front door',
    audio: 'audio/14.mp3',
    body: [
      'Everything so far bypasses the interface. The last leg pointed the real React app at the test database and drove it.',
      'The title screen found the run this harness had abandoned and narrated it — <em>"The last expedition never came home"</em> — then recovered cleanly through the abandon endpoint. Home base and the campfire rendered the harness\'s own party. Zero console errors, every request 200.',
      'And it caught something no headless suite could: the harness had been building monsters with <strong>100 health out of a maximum of 52</strong>, because the world builder set the maximum and left the current value at its default. The real UI showed it immediately.',
    ],
    metrics: [
      { value: '0', label: 'console errors', tone: 'good' },
      { value: '200', label: 'every request', tone: 'good' },
      { value: '1', label: 'harness bug found', tone: 'warn' },
    ],
    files: [
      { label: 'tools/playtest/world_setup.py', href: '../tools/playtest/world_setup.py' },
      { label: '.claude/launch.json — backend-testdb', href: '../.claude/launch.json' },
      { label: 'playtest_results/REPORT.md', href: '../playtest_results/REPORT.md' },
    ],
  },
  {
    eyebrow: 'What you can run',
    title: 'One command per surface',
    audio: 'audio/15.mp3',
    body: [
      'Zero cost, seconds each: the crash driver and the three gauntlets — the state machine, battle, every dungeon event, and the life around them. Cheap and real: the adversarial probe, the text corpora, the cost report.',
      'And when the imagination engine lands, the measurement is already written. Generate the same corpus with sparks on and compare the silence rate, the motif frequencies, the sameness ratios and the pseudo-mechanics leak against tonight\'s numbers. The baseline is a file with commands next to it.',
    ],
    table: {
      columns: ['command', 'covers', 'cost'],
      rows: [
        ['crash_driver.py --runs 100', 'state machine', '$0'],
        ['battle_gauntlet.py', 'battle promises', '$0'],
        ['dungeon_gauntlet.py', 'every path event', '$0'],
        ['life_gauntlet.py', 'chat · evolution · memory', '$0'],
        ['adversarial_probe.py', 'referee integrity', '~$0.01'],
        ['generate_text_corpus.py', 'chronicles · items', '~$0.02'],
        ['cost_report.py', 'tokens & latency', '$0'],
      ],
    },
    files: [
      { label: 'playtest_results/REPORT.md — the runbook', href: '../playtest_results/REPORT.md' },
      { label: 'tools/playtest/', href: '../tools/playtest/' },
      { label: 'docs/plans/playtest-suite-expansion.md', href: '../docs/plans/playtest-suite-expansion.md' },
    ],
  },
];
