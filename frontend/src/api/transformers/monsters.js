// Monster Transformers - SIMPLIFIED VERSION
// Pure transformation functions for monster domain objects
// Domain hooks handle response orchestration, transformers just transform data

/**
 * Transform raw monster object into clean game object
 * @param {object} rawMonster - Raw monster object from API
 * @returns {object|null} Clean monster object or null if invalid
 */
export function transformMonster(rawMonster) {
  if (!rawMonster || !rawMonster.id) {
    console.warn('Invalid monster object provided to transformer');
    return null;
  }

  return {
    // Basic info
    id: rawMonster.id,
    name: rawMonster.name,
    species: rawMonster.species,
    description: rawMonster.description,
    backstory: rawMonster.backstory,
    personalityTraits: rawMonster.personality_traits || [],

    // Identity & CMDTS (see docs/plans/monster-depth-cmdts.md)
    rarity: rawMonster.rarity || null,
    partyRole: rawMonster.party_role || null,
    generationStage: rawMonster.generation_stage || 'complete',
    taxonomy: rawMonster.taxonomy || {},
    classTaxonomy: rawMonster.class_taxonomy || [],
    ecology: rawMonster.ecology || {},
    persona: rawMonster.persona || {},
    appearance: rawMonster.appearance || {},

    // Stats (use the nested stats object if available, fallback to flat structure)
    stats: {
      attack: rawMonster.stats?.attack || rawMonster.attack || 0,
      defense: rawMonster.stats?.defense || rawMonster.defense || 0,
      speed: rawMonster.stats?.speed || rawMonster.speed || 0,
      currentHealth: rawMonster.stats?.current_health || rawMonster.current_health || 0,
      maxHealth: rawMonster.stats?.max_health || rawMonster.max_health || 0,
    },

    // Ability metadata
    abilities: transformAbilities(rawMonster.abilities || []),
    abilityCount: rawMonster.ability_count || (rawMonster.abilities || []).length,

    // Card art (simplified structure)
    cardArt: {
      exists: rawMonster.card_art?.exists || false,
      relativePath: rawMonster.card_art?.relative_path || rawMonster.card_art_path || null,
    },

    // Timestamps as Date objects
    createdAt: rawMonster.created_at ? new Date(rawMonster.created_at) : null,
    updatedAt: rawMonster.updated_at ? new Date(rawMonster.updated_at) : null,
  };
}

/**
 * Transform array of raw monsters into clean game objects
 * @param {Array} rawMonsters - Array of raw monster objects from API
 * @returns {Array} Array of clean monster objects (filters out invalid ones)
 */
export function transformMonsters(rawMonsters) {
  if (!Array.isArray(rawMonsters)) {
    console.warn('transformMonsters expects an array, received:', typeof rawMonsters);
    return [];
  }

  return rawMonsters.map(transformMonster).filter(Boolean); // Remove any null results from invalid abilities
}

/**
 * Transform raw ability object into clean game object
 * @param {object} rawAbility - Raw ability object from API
 * @returns {object|null} Clean ability object or null if invalid
 */
export function transformAbility(rawAbility) {
  if (!rawAbility || !rawAbility.id) {
    console.warn('Invalid ability object provided to transformer');
    return null;
  }

  return {
    id: rawAbility.id,
    name: rawAbility.name,
    description: rawAbility.description,
    type: rawAbility.ability_type || rawAbility.type,
    monsterId: rawAbility.monster_id,
    createdAt: rawAbility.created_at ? new Date(rawAbility.created_at) : null,
    updatedAt: rawAbility.updated_at ? new Date(rawAbility.updated_at) : null,
  };
}

/**
 * Transform array of raw abilities into clean game objects
 * @param {Array} rawAbilities - Array of raw ability objects from API
 * @returns {Array} Array of clean ability objects (filters out invalid ones)
 */
export function transformAbilities(rawAbilities) {
  if (!Array.isArray(rawAbilities)) {
    console.warn('transformAbilities expects an array, received:', typeof rawAbilities);
    return [];
  }

  return rawAbilities.map(transformAbility).filter(Boolean); // Remove any null results from invalid abilities
}

/**
 * Transform a raw monster memory into frontend shape
 * @param {object} rawMemory - Raw memory from monster.memory_added / the memories endpoint
 * @returns {object|null} Clean memory object
 */
export function transformMemory(rawMemory) {
  if (!rawMemory || !rawMemory.id) {
    console.warn('Invalid memory object provided to transformer');
    return null;
  }

  return {
    id: rawMemory.id,
    monsterId: rawMemory.monster_id,
    runId: rawMemory.run_id,
    runNumber: rawMemory.details?.run_number ?? null,
    kind: rawMemory.kind,
    content: rawMemory.content,
    details: rawMemory.details || {},
    createdAt: rawMemory.created_at ? new Date(rawMemory.created_at) : null,
  };
}

/**
 * Transform array of raw memories into clean game objects
 * @param {Array} rawMemories - Array of raw memory objects from API
 * @returns {Array} Array of clean memory objects (filters out invalid ones)
 */
export function transformMemories(rawMemories) {
  if (!Array.isArray(rawMemories)) return [];
  return rawMemories.map(transformMemory).filter(Boolean);
}

/**
 * Transform a raw evolution lineage record into frontend shape
 * @param {object} rawEvolution - Raw evolution from monster.evolved / the evolutions endpoint
 * @returns {object|null} Clean evolution object
 */
export function transformEvolution(rawEvolution) {
  if (!rawEvolution || !rawEvolution.id) {
    console.warn('Invalid evolution object provided to transformer');
    return null;
  }

  return {
    id: rawEvolution.id,
    monsterId: rawEvolution.monster_id,
    stage: rawEvolution.stage,
    guidance: rawEvolution.guidance || null,
    narrative: rawEvolution.narrative || null,
    oldName: rawEvolution.old_name,
    oldSpecies: rawEvolution.old_species,
    oldRarity: rawEvolution.old_rarity || null,
    newName: rawEvolution.new_name,
    newSpecies: rawEvolution.new_species,
    newRarity: rawEvolution.new_rarity,
    oldStats: {
      maxHealth: rawEvolution.old_stats?.max_health ?? 0,
      attack: rawEvolution.old_stats?.attack ?? 0,
      defense: rawEvolution.old_stats?.defense ?? 0,
      speed: rawEvolution.old_stats?.speed ?? 0,
    },
    appliedBoostPct: rawEvolution.applied_boost_pct ?? 0,
    oldCardArtPath: rawEvolution.old_card_art_path || null,
    details: rawEvolution.details || {},
    createdAt: rawEvolution.created_at ? new Date(rawEvolution.created_at) : null,
  };
}

/**
 * Transform array of raw evolutions into clean game objects
 * @param {Array} rawEvolutions - Array of raw evolution objects from API
 * @returns {Array} Array of clean evolution objects (filters out invalid ones)
 */
export function transformEvolutions(rawEvolutions) {
  if (!Array.isArray(rawEvolutions)) return [];
  return rawEvolutions.map(transformEvolution).filter(Boolean);
}

/**
 * Transform monster statistics object into clean format
 * @param {object} rawStats - Raw monster statistics from API
 * @returns {object} Clean monster statistics object
 */
export function transformMonsterStats(rawStats) {
  if (!rawStats || typeof rawStats !== 'object') {
    console.warn('Invalid monster stats object provided to transformer');
    return {
      overview: {
        totalMonsters: 0,
        totalAbilities: 0,
        uniqueSpecies: 0,
        withCardArt: 0,
        withoutCardArt: 0,
        avgAbilitiesPerMonster: 0,
        cardArtPercentage: 0,
      },
      speciesBreakdown: {},
    };
  }

  return {
    overview: {
      totalMonsters: rawStats.total_monsters || 0,
      totalAbilities: rawStats.total_abilities || 0,
      uniqueSpecies: rawStats.unique_species || 0,
      withCardArt: rawStats.with_card_art || 0,
      withoutCardArt: rawStats.without_card_art || 0,
      avgAbilitiesPerMonster: rawStats.avg_abilities_per_monster || 0,
      cardArtPercentage: rawStats.card_art_percentage || 0,
    },

    speciesBreakdown: rawStats.species_breakdown || {},

    // Transform featured monsters if they exist
    newestMonster: rawStats.newest_monster ? transformMonster(rawStats.newest_monster) : null,
    oldestMonster: rawStats.oldest_monster ? transformMonster(rawStats.oldest_monster) : null,
  };
}
