// Game State Helper Functions
// Pure utility functions for game state management and filtering
// Keeps UI logic separate from business logic

/**
 * Filter following monsters to exclude those currently in active party
 * @param {Array} followingMonsters - All monsters in player's collection
 * @param {Array} activeParty - Monsters currently in active party
 * @returns {Array} Available monsters for pool (not in party)
 */
export function getAvailablePoolMonsters(followingMonsters, activeParty) {
  if (!followingMonsters || !Array.isArray(followingMonsters)) return [];
  if (!activeParty || !Array.isArray(activeParty)) return followingMonsters;
  
  const partyIds = new Set(activeParty.map(monster => monster.id));
  return followingMonsters.filter(monster => !partyIds.has(monster.id));
}

/**
 * Check if a specific monster is currently in the active party
 * @param {Object} monster - Monster to check
 * @param {Array} activeParty - Current active party
 * @returns {boolean} True if monster is in party
 */
export function isMonsterInParty(monster, activeParty) {
  if (!monster || !activeParty || !Array.isArray(activeParty)) return false;
  return activeParty.some(partyMonster => partyMonster.id === monster.id);
}

/**
 * Calculate pagination info for filtered monster list
 * @param {Array} monsters - List of monsters to paginate
 * @param {number} currentPage - Current page number (1-based)
 * @param {number} itemsPerPage - Number of items per page
 * @returns {Object} Pagination info and paginated items
 */
export function getPaginatedMonsters(monsters, currentPage, itemsPerPage) {
  const totalItems = monsters.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  
  return {
    items: monsters.slice(startIndex, endIndex),
    totalItems,
    totalPages,
    currentPage,
    hasNext: currentPage < totalPages,
    hasPrevious: currentPage > 1,
    startIndex: startIndex + 1, // 1-based for display
    endIndex: Math.min(endIndex, totalItems) // don't exceed total
  };
}

/**
 * Validate party size constraints
 * @param {Array} activeParty - Current active party
 * @param {number} maxPartySize - Maximum allowed party size (default: 4)
 * @returns {Object} Party validation info
 */
export function validatePartySize(activeParty, maxPartySize = 4) {
  const currentSize = activeParty ? activeParty.length : 0;
  
  return {
    currentSize,
    maxSize: maxPartySize,
    isFull: currentSize >= maxPartySize,
    canAddMore: currentSize < maxPartySize,
    spotsRemaining: Math.max(0, maxPartySize - currentSize)
  };
}