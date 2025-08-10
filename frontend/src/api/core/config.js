// API Configuration - Single source of truth for all API settings
// Updated to match complete backend API reference guide
// Centralizes URLs, timeouts, and endpoint definitions

// Base configuration
export const API_CONFIG = {
  BASE_URL: 'http://localhost:5000',
  DEFAULT_TIMEOUT: 600000, // 10 minutes
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  }
};

// Complete API endpoint paths - organized by feature area and matching backend exactly
export const API_ENDPOINTS = {
  // ===== SYSTEM & HEALTH =====
  HEALTH: '/api/health',
  GAME_STATUS: '/api/game/status',
  
  // ===== MONSTER MANAGEMENT =====
  MONSTERS: '/api/monsters',
  MONSTERS_GENERATE: '/api/monsters/generate',
  MONSTERS_BY_ID: (id) => `/api/monsters/${id}`,
  MONSTERS_TEMPLATES: '/api/monsters/templates',
  MONSTERS_STATS: '/api/monsters/stats',
  
  // Monster abilities
  MONSTER_ABILITIES: (id) => `/api/monsters/${id}/abilities`,
  MONSTER_GENERATE_ABILITY: (id) => `/api/monsters/${id}/abilities`,
  
  // Monster card art
  MONSTER_GENERATE_CARD_ART: (id) => `/api/monsters/${id}/card-art`,
  MONSTER_GET_CARD_ART: (id) => `/api/monsters/${id}/card-art`,
  MONSTER_CARD_ART_FILE: (path) => `/api/monsters/card-art/${path}`,
  
  // ===== GAME STATE MANAGEMENT =====
  GAME_STATE: '/api/game-state',
  GAME_STATE_RESET: '/api/game-state/reset',
  
  // Following monsters
  FOLLOWING: '/api/game-state/following',
  FOLLOWING_ADD: '/api/game-state/following/add',
  FOLLOWING_REMOVE: '/api/game-state/following/remove',
  
  // Active party
  PARTY: '/api/game-state/party',
  PARTY_SET: '/api/game-state/party/set',
  PARTY_READY: '/api/game-state/party/ready',
  
  // ===== DUNGEON SYSTEM =====
  DUNGEON_STATUS: '/api/dungeon/status',
  DUNGEON_STATE: '/api/dungeon/state',
  DUNGEON_ENTER: '/api/dungeon/enter',
  DUNGEON_CHOOSE_DOOR: '/api/dungeon/choose-door',
  
  // ===== GENERATION SYSTEM (New Unified System) =====
  GENERATION_STATUS: '/api/generation/status',
  GENERATION_LOGS: '/api/generation/logs',
  GENERATION_LOG_DETAIL: (id) => `/api/generation/logs/${id}`,
  GENERATION_STATS: '/api/generation/stats',
  GENERATION_LOG_OPTIONS: '/api/generation/log-options',
  
  // ===== STREAMING & REAL-TIME =====
  STREAMING_EVENTS: '/api/streaming/llm-events',
  
  // ===== TESTING & DEBUG =====
  GAME_TESTER_TESTS: '/api/game_tester/tests',
  GAME_TESTER_RUN: (testName) => `/api/game_tester/run/${testName}`
  
};

// Environment-specific overrides
export const getApiConfig = () => {
  const config = { ...API_CONFIG };
  
  // Development-specific settings
  if (process.env.NODE_ENV === 'development') {
    config.ENABLE_LOGGING = true;
    config.LOG_REQUESTS = true;
    config.LOG_RESPONSES = true;
  }
  
  // Production overrides
  if (process.env.NODE_ENV === 'production') {
    config.ENABLE_LOGGING = false;
    config.BASE_URL = process.env.REACT_APP_API_URL || config.BASE_URL;
  }
  
  return config;
};