// Monster Transformers - Clean API responses into usable game objects
// Handles all monster-related API response transformation
// Converts snake_case to camelCase and simplifies nested structures

/**
 * Transform raw monster API object into clean game object
 * @param {object} rawMonster - Raw monster object from API
 * @returns {object} Clean monster object
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

    // Stats (use the nested stats object, it's more reliable)
    stats: {
      attack: rawMonster.stats?.attack || rawMonster.attack || 0,
      defense: rawMonster.stats?.defense || rawMonster.defense || 0,
      speed: rawMonster.stats?.speed || rawMonster.speed || 0,
      currentHealth: rawMonster.stats?.current_health || rawMonster.current_health || 0,
      maxHealth: rawMonster.stats?.max_health || rawMonster.max_health || 0
    },

    // Abilities (transform to camelCase)
    abilities: (rawMonster.abilities || []).map(transformAbility),
    abilityCount: rawMonster.ability_count || rawMonster.abilities?.length || 0,

    // Card art (simplified structure, keep relative path)
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
 * Transform raw ability API object into clean game object
 * @param {object} rawAbility - Raw ability object from API
 * @returns {object} Clean ability object
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
    type: rawAbility.ability_type,
    monsterId: rawAbility.monster_id,
    createdAt: rawAbility.created_at ? new Date(rawAbility.created_at) : null,
    updatedAt: rawAbility.updated_at ? new Date(rawAbility.updated_at) : null
  };
}

/**
 * Transform monster collection API response
 * @param {object} rawResponse - Raw API response from loadMonsters
 * @returns {object} Clean collection object
 */
export function transformMonsterCollection(rawResponse) {
  if (!rawResponse || !rawResponse.success) {
    console.warn('Invalid monster collection response provided to transformer');
    return {
      monsters: [],
      pagination: { total: 0, hasMore: false, nextOffset: null },
      filters: { type: 'all', sortBy: 'newest' }
    };
  }

  return {
    monsters: (rawResponse.monsters || []).map(transformMonster).filter(Boolean),
    
    pagination: {
      total: rawResponse.total || 0,
      hasMore: rawResponse.pagination?.has_more || false,
      nextOffset: rawResponse.pagination?.next_offset || null,
      currentOffset: rawResponse.pagination?.offset || 0,
      limit: rawResponse.pagination?.limit || 50
    },
    
    filters: {
      type: rawResponse.filters_applied?.filter_type || 'all',
      sortBy: rawResponse.filters_applied?.sort_by || 'newest'
    }
  };
}

/**
 * Transform monster stats API response
 * @param {object} rawResponse - Raw API response from loadMonsterStats
 * @returns {object} Clean stats object
 */
export function transformMonsterStats(rawResponse) {
  if (!rawResponse || !rawResponse.success) {
    console.warn('Invalid monster stats response provided to transformer');
    return null;
  }

  const stats = rawResponse.stats || {};

  return {
    filterApplied: rawResponse.filter_applied || 'all',
    
    overview: {
      totalMonsters: stats.total_monsters || 0,
      totalAbilities: stats.total_abilities || 0,
      uniqueSpecies: stats.unique_species || 0,
      withCardArt: stats.with_card_art || 0,
      withoutCardArt: stats.without_card_art || 0,
      avgAbilitiesPerMonster: stats.avg_abilities_per_monster || 0,
      cardArtPercentage: stats.card_art_percentage || 0
    },
    
    speciesBreakdown: stats.species_breakdown || {},
    
    // Transform featured monsters if they exist
    newestMonster: stats.newest_monster ? transformMonster(stats.newest_monster) : null,
    oldestMonster: stats.oldest_monster ? transformMonster(stats.oldest_monster) : null,
    
    // Include context data if filtering was applied
    context: rawResponse.context || null
  };
}

/**
 * Transform abilities collection API response
 * @param {object} rawResponse - Raw API response from getMonsterAbilities
 * @returns {object} Clean abilities object
 */
export function transformAbilitiesCollection(rawResponse) {
  if (!rawResponse || !rawResponse.success) {
    console.warn('Invalid abilities collection response provided to transformer');
    return {
      abilities: [],
      count: 0,
      monsterId: null
    };
  }

  return {
    abilities: (rawResponse.abilities || []).map(transformAbility).filter(Boolean),
    count: rawResponse.count || rawResponse.abilities?.length || 0,
    monsterId: rawResponse.monster_id || null
  };
}

/**
 * Transform card art API response
 * @param {object} rawResponse - Raw API response from getMonsterCardArt
 * @returns {object} Clean card art object
 */
export function transformCardArt(rawResponse) {
  if (!rawResponse || !rawResponse.success) {
    console.warn('Invalid card art response provided to transformer');
    return {
      exists: false,
      relativePath: null,
      monsterId: null
    };
  }

  const cardArt = rawResponse.card_art || {};

  return {
    exists: cardArt.exists || false,
    relativePath: cardArt.relative_path || null,
    monsterId: rawResponse.monster_id || null
  };
}

/**
 * Transform monster templates API response
 * @param {object} rawResponse - Raw API response from getMonsterTemplates
 * @returns {object} Clean templates object
 */
export function transformMonsterTemplates(rawResponse) {
  if (!rawResponse || !rawResponse.success) {
    console.warn('Invalid monster templates response provided to transformer');
    return {};
  }

  return rawResponse.templates || {};
}

/**
 * Transform individual monster API response (for getMonster)
 * @param {object} rawResponse - Raw API response from getMonster
 * @returns {object|null} Clean monster object or null
 */
export function transformMonsterResponse(rawResponse) {
  if (!rawResponse || !rawResponse.success) {
    console.warn('Invalid monster response provided to transformer');
    return null;
  }

  return transformMonster(rawResponse.monster);
}

/**
 * Transform monster generation API response
 * @param {object} rawResponse - Raw API response from generateMonster
 * @returns {object} Clean generation result
 */
export function transformMonsterGeneration(rawResponse) {
  if (!rawResponse || !rawResponse.success) {
    console.warn('Invalid monster generation response provided to transformer');
    return {
      success: false,
      error: rawResponse?.error || 'Unknown generation error',
      monster: null
    };
  }

  return {
    success: true,
    monster: rawResponse.monster ? transformMonster(rawResponse.monster) : null,
    requestId: rawResponse.request_id || null,
    logId: rawResponse.log_id || null
  };
}

/**
 * Transform ability generation API response
 * @param {object} rawResponse - Raw API response from generateAbility
 * @returns {object} Clean ability generation result
 */
export function transformAbilityGeneration(rawResponse) {
  if (!rawResponse || !rawResponse.success) {
    console.warn('Invalid ability generation response provided to transformer');
    return {
      success: false,
      error: rawResponse?.error || 'Unknown generation error',
      ability: null
    };
  }

  return {
    success: true,
    ability: rawResponse.ability ? transformAbility(rawResponse.ability) : null,
    requestId: rawResponse.request_id || null,
    logId: rawResponse.log_id || null
  };
}