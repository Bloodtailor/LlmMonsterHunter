// useEventSource Hook - Generic Server-Sent Events hook
// Like useAsyncState but for SSE connections
// Processes events through a registry system for scalability

import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Generic hook for managing Server-Sent Events connections
 * Processes events through a configurable registry system
 * 
 * @param {string} url - SSE endpoint URL
 * @param {object} eventRegistry - Registry of event configurations
 * @param {object} options - Hook options
 * @param {boolean} options.autoConnect - Auto-connect on mount (default: true)
 * @param {number} options.reconnectDelay - Delay before reconnection (default: 5000ms)
 * @param {object} options.initialState - Initial state object (default: {})
 * @returns {object} SSE state and controls
 */
export function useEventSource(url, eventRegistry, options = {}) {
  const {
    autoConnect = true,
    reconnectDelay = 5000,
    initialState = {}
  } = options;

  // Connection state (similar to useAsyncState)
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  
  // Event data state (flexible structure defined by registry)
  const [eventState, setEventState] = useState({
    lastActivity: null,
    ...initialState
  });
  
  // Refs for cleanup
  const eventSourceRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Generic event processor - the heart of the registry system
  const processEvent = useCallback((eventType, rawEvent) => {
    const eventConfig = eventRegistry[eventType];
    
    if (!eventConfig) {
      console.warn(`Unknown event type: ${eventType}`);
      return;
    }

    console.warn(`Recieved event type: ${eventType}`);

    try {
      // Parse raw SSE data
      const rawData = JSON.parse(rawEvent.data);
      
      // Apply transformation using registry
      const transformedData = eventConfig.transform ? 
        eventConfig.transform(rawData) : 
        rawData;
      
      // Update state using registry logic
      setEventState(currentState => {
        const updatedState = eventConfig.updateState ? 
          eventConfig.updateState(currentState, transformedData) :
          { ...currentState, [eventType]: transformedData };
        
        // Always update last activity
        return {
          ...updatedState,
          lastActivity: new Date()
        };
      });
      
    } catch (error) {
      console.error(`Error processing ${eventType} event:`, error);
      // Could add error state management here if needed
    }
  }, [eventRegistry]);

  // Connect to EventSource
  const connect = useCallback(() => {
    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    try {
      console.log('🔗 Connecting to EventSource:', url);
      
      const eventSource = new EventSource('http://localhost:5000/api/streaming/llm-events');
      eventSourceRef.current = eventSource;

      // Standard connection handlers
      eventSource.onopen = () => {
        console.log('✅ EventSource connected');
        setIsConnected(true);
        setConnectionError(null);
        setEventState(prev => ({ ...prev, lastActivity: new Date() }));
      };

      eventSource.onerror = (error) => {
        console.error('❌ EventSource error:', error);
        setIsConnected(false);
        setConnectionError('Connection lost');
        
        // Auto-reconnect after delay
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          connect();
        }, reconnectDelay);
      };

      // Register all events from registry automatically
      Object.keys(eventRegistry).forEach(eventType => {
        console.warn('registering event type: ', eventType)
        eventSource.addEventListener(eventType, (rawEvent) => {
          processEvent(eventType, rawEvent);
        });
      });

    } catch (error) {
      console.error('❌ Failed to create EventSource:', error);
      setConnectionError(error.message);
    }
  }, [url, eventRegistry, processEvent, reconnectDelay]);

  // Disconnect from EventSource
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionError(null);
  }, []);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    
    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Return interface similar to useAsyncState
  return {
    // Connection state (like isLoading, isError in useAsyncState)
    isConnected,
    connectionError,
    
    // Event data (flexible structure from registry)
    ...eventState,
    
    // Connection controls (like execute in useAsyncState)
    connect,
    disconnect,
    
    // For debugging
    eventSource: eventSourceRef.current
  };
}