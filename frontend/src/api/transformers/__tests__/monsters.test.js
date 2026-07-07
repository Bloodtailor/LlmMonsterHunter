// Monster transformer tests - the snake_case -> camelCase boundary.
// Pattern-setter for frontend tests: pure functions, no mocks needed
// (console.warn silenced where invalid input is the point of the test).

import {
  transformAbility,
  transformEvolution,
  transformMemory,
  transformMonster,
  transformMonsters,
} from '../monsters.js';

const RAW_MONSTER = {
  id: 7,
  name: 'Rokk',
  species: 'Pebble Golem',
  description: 'A patient pile of pebbles.',
  backstory: 'It watched the mountain.',
  personality_traits: ['patient'],
  rarity: 'uncommon',
  party_role: 'guardian',
  generation_stage: 'complete',
  taxonomy: { domain: 'Materium' },
  stats: { attack: 20, defense: 16, speed: 12, current_health: 90, max_health: 100 },
  abilities: [
    { id: 1, name: 'Stone Wall', description: 'Shelters an ally.', ability_type: 'defense' },
  ],
  card_art: { exists: true, relative_path: 'monster_card_art/rokk.png' },
  created_at: '2026-07-01T12:00:00',
};

describe('transformMonster', () => {
  it('maps snake_case fields to camelCase', () => {
    const monster = transformMonster(RAW_MONSTER);
    expect(monster.id).toBe(7);
    expect(monster.personalityTraits).toEqual(['patient']);
    expect(monster.partyRole).toBe('guardian');
    expect(monster.stats.maxHealth).toBe(100);
    expect(monster.stats.currentHealth).toBe(90);
    expect(monster.cardArt).toEqual({ exists: true, relativePath: 'monster_card_art/rokk.png' });
    expect(monster.createdAt).toBeInstanceOf(Date);
  });

  it('reads flat legacy stats when the nested object is missing', () => {
    const monster = transformMonster({ id: 1, name: 'X', attack: 5, max_health: 40 });
    expect(monster.stats.attack).toBe(5);
    expect(monster.stats.maxHealth).toBe(40);
  });

  it('transforms nested abilities and counts them', () => {
    const monster = transformMonster(RAW_MONSTER);
    expect(monster.abilities).toHaveLength(1);
    expect(monster.abilities[0].type).toBe('defense');
    expect(monster.abilityCount).toBe(1);
  });

  it('returns null (with a warning) for objects without an id', () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => {});
    expect(transformMonster(null)).toBeNull();
    expect(transformMonster({ name: 'No Id' })).toBeNull();
    warn.mockRestore();
  });
});

describe('transformMonsters', () => {
  it('filters invalid entries out of the list', () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => {});
    const monsters = transformMonsters([RAW_MONSTER, null, { name: 'ghost' }]);
    expect(monsters).toHaveLength(1);
    warn.mockRestore();
  });

  it('answers non-arrays with an empty list', () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => {});
    expect(transformMonsters('nope')).toEqual([]);
    warn.mockRestore();
  });
});

describe('transformAbility', () => {
  it('prefers ability_type over type', () => {
    const ability = transformAbility({ id: 2, name: 'Gust', ability_type: 'movement', type: 'x' });
    expect(ability.type).toBe('movement');
  });
});

describe('transformMemory', () => {
  it('lifts run_number out of details', () => {
    const memory = transformMemory({
      id: 3,
      monster_id: 7,
      run_id: 11,
      kind: 'was_defeated',
      content: 'Fell at the gate.',
      details: { run_number: 4 },
    });
    expect(memory.runNumber).toBe(4);
    expect(memory.kind).toBe('was_defeated');
  });
});

describe('transformEvolution', () => {
  it('maps the lineage snapshot with defaults', () => {
    const evolution = transformEvolution({
      id: 5,
      monster_id: 7,
      stage: 1,
      old_name: 'Rokk',
      old_species: 'Pebble Golem',
      new_name: 'Rokkarath',
      new_species: 'Basalt Colossus',
      new_rarity: 'uncommon',
      old_stats: { max_health: 100, attack: 20 },
      applied_boost_pct: 0.25,
    });
    expect(evolution.oldStats).toEqual({ maxHealth: 100, attack: 20, defense: 0, speed: 0 });
    expect(evolution.appliedBoostPct).toBe(0.25);
    expect(evolution.oldRarity).toBeNull();
  });
});
