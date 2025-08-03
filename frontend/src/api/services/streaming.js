// Streaming API Service - Minimal service for SSE endpoint
// Just exports the URL constant for EventSource connections

import { API_ENDPOINTS } from '../core/config.js';

// ===== STREAMING EVENTS URL =====

/**
 * SSE endpoint URL for real-time streaming events
 * Use with EventSource, not fetch/axios
 */
export const STREAMING_EVENTS_URL = `http://localhost:5000${API_ENDPOINTS.STREAMING_EVENTS}`;