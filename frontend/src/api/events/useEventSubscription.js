// useEventSubscription - React hook for subscribing to specific broadcast events
// Lets the smallest component react to exactly one event without re-rendering on others
// The handler is kept in a ref so callers can pass inline functions safely

import { useEffect, useRef } from 'react';
import { subscribeToEvent } from '../core/eventBroadcast.js';

/**
 * Subscribe to a broadcast event for the lifetime of the component
 * @param {string} eventName - Broadcast event name (e.g., 'workflowCompleted') or '*' for all events
 * @param {function} handler - Called with (eventData, eventName) when the event fires
 */
export const useEventSubscription = (eventName, handler) => {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    const unsubscribe = subscribeToEvent(eventName, (eventData, firedEventName) => {
      handlerRef.current(eventData, firedEventName);
    });
    return unsubscribe;
  }, [eventName]);
};
