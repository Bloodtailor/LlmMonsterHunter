// Event Broadcasting System - Routes events to domain stores and event subscribers
// Two consumption paths:
//   1. Domain routers - update external state stores (aiStateStore, workflowStateStore)
//   2. Subscriber registry - components subscribe to specific events via subscribeToEvent
// Keeps SSE events separate from computed state management

import { aiStatusRouter } from "../stores/aiStateStore";
import { workflowStatusRouter } from "../stores/workflowStateStore.js";

// ===== EVENT SUBSCRIBER REGISTRY =====
// eventName -> Set of callbacks. Use '*' to subscribe to every event.
const subscribers = new Map();

/**
 * Subscribe to a specific broadcast event
 * @param {string} eventName - Broadcast event name (e.g., 'llmGenerationUpdate') or '*' for all events
 * @param {function} callback - Called with (eventData, eventName) when the event fires
 * @returns {function} Unsubscribe function
 */
export const subscribeToEvent = (eventName, callback) => {
  if (!subscribers.has(eventName)) {
    subscribers.set(eventName, new Set());
  }
  subscribers.get(eventName).add(callback);

  return () => {
    const callbacks = subscribers.get(eventName);
    if (callbacks) {
      callbacks.delete(callback);
      if (callbacks.size === 0) {
        subscribers.delete(eventName);
      }
    }
  };
};

// Notify exact-match and wildcard subscribers (continue if one fails)
const notifySubscribers = (eventName, eventData) => {
  const exact = subscribers.get(eventName);
  const wildcard = subscribers.get('*');

  [...(exact || []), ...(wildcard || [])].forEach(callback => {
    try {
      callback(eventData, eventName);
    } catch (error) {
      console.error(`Event subscriber failed for ${eventName}:`, error);
    }
  });
};

/**
 * Central event broadcaster - routes events to domain-specific state stores,
 * then notifies any component-level subscribers
 * @param {string} eventName - The name of the event (e.g., 'llmGenerationStarted')
 * @param {object} eventData - Transformed event data
 */
export const broadcastEvent = (eventName, eventData) => {
  // Route to domain state stores
  aiStatusRouter(eventName, eventData);
  workflowStatusRouter(eventName, eventData);

  // Notify fine-grained event subscribers
  notifySubscribers(eventName, eventData);
};
