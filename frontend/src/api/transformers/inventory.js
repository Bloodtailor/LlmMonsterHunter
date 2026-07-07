// Inventory Transformers
// Pure transformation functions for items and CoCaTok keepsakes

/**
 * Transform raw item object into clean game object
 * @param {object} rawItem - Raw item object from API
 * @returns {object|null} Clean item object or null if invalid
 */
export function transformItem(rawItem) {
  if (!rawItem || !rawItem.id) {
    console.warn('Invalid item object provided to transformer');
    return null;
  }

  return {
    id: rawItem.id,
    name: rawItem.name,
    description: rawItem.description,
    emoji: rawItem.emoji || '🎁',
    usesRemaining: rawItem.uses_remaining ?? 1,
    sourceNote: rawItem.source_note || null,
    createdAt: rawItem.created_at ? new Date(rawItem.created_at) : null,
  };
}

/**
 * Transform raw CoCaTok object into clean game object
 * @param {object} rawCoCaTok - Raw CoCaTok object from API
 * @returns {object|null} Clean CoCaTok object or null if invalid
 */
export function transformCoCaTok(rawCoCaTok) {
  if (!rawCoCaTok || !rawCoCaTok.id) {
    console.warn('Invalid CoCaTok object provided to transformer');
    return null;
  }

  return {
    id: rawCoCaTok.id,
    title: rawCoCaTok.title,
    emoji: rawCoCaTok.emoji || '🏆',
    color: rawCoCaTok.color || 'purple-mystic',
    commemoration: rawCoCaTok.commemoration,
    eventType: rawCoCaTok.event_type || 'battle_victory',
    locationName: rawCoCaTok.location_name || null,
    earnedAt: rawCoCaTok.created_at ? new Date(rawCoCaTok.created_at) : null,
  };
}

/**
 * Transform an array of raw inventory entries by kind
 * @param {Array} rawEntries - Raw entries from the inventory API
 * @param {string} kind - 'items' | 'cocatoks'
 * @returns {Array} Clean entries (invalid ones filtered out)
 */
export function transformInventoryEntries(rawEntries, kind) {
  if (!Array.isArray(rawEntries)) {
    console.warn('transformInventoryEntries expects an array, received:', typeof rawEntries);
    return [];
  }

  const transform = kind === 'cocatoks' ? transformCoCaTok : transformItem;
  return rawEntries.map(transform).filter(Boolean);
}
