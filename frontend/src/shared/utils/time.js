// Time Utility Functions - Simple formatting helpers
// Used across streaming components for consistent time display

/**
 * Format timestamp to local time string
 * @param {Date|string|number} timestamp - Timestamp to format
 * @returns {string} Formatted time string (e.g., "2:30:45 PM")
 */
export function formatTime(timestamp) {
  if (!timestamp) return '--';
  return new Date(timestamp).toLocaleTimeString();
}

/**
 * Format duration in seconds to readable string
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration (e.g., "2.45s")
 */
export function formatDuration(seconds) {
  if (!seconds) return '--';
  return `${seconds.toFixed(2)}s`;
}