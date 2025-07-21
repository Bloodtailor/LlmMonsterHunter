// API Configuration - Single source of truth for all API settings
// Centralizes URLs, timeouts, and other API-related constants

// Base configuration
export const API_CONFIG = {
  BASE_URL: 'http://localhost:5000',
  DEFAULT_TIMEOUT: 5000, // 5 seconds
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  }
};

// API endpoint paths - organized by feature area
export const API_ENDPOINTS = {
  // System & Health
  HEALTH: '/api/health',
  GAME_STATUS: '/api/game/status',
  
  // Game State Management
  GAME_STATE: '/api/game-state',
  GAME_STATE_RESET: '/api/game-state/reset',
  FOLLOWING: '/api/game-state/following',
  FOLLOWING_ADD: '/api/game-state/following/add',
  FOLLOWING_REMOVE: '/api/game-state/following/remove',
  PARTY: '/api/game-state/party',
  PARTY_SET: '/api/game-state/party/set',
  PARTY_READY: '/api/game-state/party/ready',
  
  // Monster Management
  MONSTERS: '/api/monsters',
  MONSTERS_GENERATE: '/api/monsters/generate',
  MONSTERS_STATS: '/api/monsters/stats',
  MONSTERS_CARD_ART: '/api/monsters/card-art',
  MONSTER_ABILITIES: (id) => `/api/monsters/${id}/abilities`,
  
  // Dungeon System
  DUNGEON_STATUS: '/api/dungeon/status',
  DUNGEON_STATE: '/api/dungeon/state',
  DUNGEON_ENTER: '/api/dungeon/enter',
  DUNGEON_CHOOSE_DOOR: '/api/dungeon/choose-door',
  
  // LLM & Generation System
  LLM_STATUS: '/api/llm/status',
  LLM_LOGS: '/api/llm/logs',
  LLM_LOG_DETAIL: (id) => `/api/llm/logs/${id}`,
  LLM_STATS: '/api/llm/stats',
  LLM_PROMPTS: '/api/llm/prompts',
  LLM_CURRENT_GENERATION: '/api/llm/current-generation',
  
  // Generation Logs (new system)
  GENERATION_LOGS: '/api/generation/logs',
  
  // Streaming & Real-time
  STREAMING_EVENTS: '/api/streaming/llm-events',
  STREAMING_TEST: '/api/streaming/test/simple',
  
  // Testing & Debug
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
  
  // Production overrides could go here
  if (process.env.NODE_ENV === 'production') {
    config.ENABLE_LOGGING = false;
    config.BASE_URL = process.env.REACT_APP_API_URL || config.BASE_URL;
  }
  
  return config;
};