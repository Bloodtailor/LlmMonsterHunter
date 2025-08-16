import { useEffect, useState, useRef, useCallback } from 'react';

const SSE_URL = 'http://localhost:5000/api/sse/events';

export const useSSE = (eventHandlers) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const eventSourceRef = useRef(null);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsConnected(false);
    setConnectionError(null);
  }, []);

  const connect = useCallback(() => {
    if (!eventHandlers) {
      return;
    }

    // Close existing connection if any
    disconnect();

    // Create EventSource connection
    const eventSource = new EventSource(SSE_URL);
    eventSourceRef.current = eventSource;

    // Handle connection opened
    eventSource.onopen = () => {
      setIsConnected(true);
      setConnectionError(null);
    };

    // Handle connection errors
    eventSource.onerror = (error) => {
      setIsConnected(false);
      setConnectionError(error);
    };

    // Register all event handlers with automatic JSON parsing
    Object.entries(eventHandlers).forEach(([eventType, handler]) => {
      eventSource.addEventListener(eventType, (event) => {
        try {
          // Automatically parse JSON for all event handlers
          const eventData = JSON.parse(event.data);
          // Call the handler with parsed eventData instead of raw event
          handler(eventData);
        } catch (parseError) {
          console.error(`Failed to parse JSON for event ${eventType}:`, parseError);
        }
      });
    });
  }, [eventHandlers, disconnect]);

  // Auto-connect on mount and disconnect on unmount
  useEffect(() => {
    connect();
    
    // Cleanup function - disconnect on unmount
    return disconnect;
  }, []);

  return {
    isConnected,
    connectionError,
    connect,
    disconnect
  };
};