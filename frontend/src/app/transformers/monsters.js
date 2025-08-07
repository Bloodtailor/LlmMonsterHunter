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

    // Stats (use the nested stats object if available, fallback to flat structure)
    stats: {
      attack: rawMonster.stats?.attack || rawMonster.attack || 0,
      defense: rawMonster.stats?.defense || rawMonster.defense || 0,
      speed: rawMonster.stats?.speed || rawMonster.speed || 0,
      currentHealth: rawMonster.stats?.current_health || rawMonster.current_health || 0,
      maxHealth: rawMonster.stats?.max_health || rawMonster.max_health || 0
    },

    // Ability metadata
    abilities: transformAbilities(rawMonster.abilities || []),
    abilityCount: rawMonster.ability_count || (rawMonster.abilities || []).length,

    // Card art (simplified structure)
    cardArt: {
      exists: rawMonster.card_art?.exists || false,
      relativePath: rawMonster.card_art?.relative_path || rawMonster.card_art_path || null
    },

    // Timestamps as Date objects
    createdAt: rawMonster.created_at ? new Date(rawMonster.created_at) : null,
    updatedAt: rawMonster.updated_at ? new Date(rawMonster.updated_at) : null
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

  return rawMonsters
    .map(transformMonster)
    .filter(Boolean); // Remove any null results from invalid abilities

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
    updatedAt: rawAbility.updated_at ? new Date(rawAbility.updated_at) : null
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

  return rawAbilities
    .map(transformAbility)
    .filter(Boolean); // Remove any null results from invalid abilities
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
        cardArtPercentage: 0
      },
      speciesBreakdown: {}
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
      cardArtPercentage: rawStats.card_art_percentage || 0
    },
    
    speciesBreakdown: rawStats.species_breakdown || {},
    
    // Transform featured monsters if they exist
    newestMonster: rawStats.newest_monster ? transformMonster(rawStats.newest_monster) : null,
    oldestMonster: rawStats.oldest_monster ? transformMonster(rawStats.oldest_monster) : null
  };
}