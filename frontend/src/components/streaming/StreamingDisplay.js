// Streaming Display Component
// Always-visible overlay showing real-time LLM generation progress
// Connects to backend SSE stream and displays current generation

import React, { useState, useEffect, useRef } from 'react';

function StreamingDisplay() {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [currentGeneration, setCurrentGeneration] = useState(null);
  const [queueStatus, setQueueStatus] = useState(null);
  const [isMinimized, setIsMinimized] = useState(false);
  const [lastActivity, setLastActivity] = useState(null);
  
  const eventSourceRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const autoHideTimeoutRef = useRef(null);

  // Connect to SSE stream
  useEffect(() => {
    connectToStream();
    
    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (autoHideTimeoutRef.current) {
        clearTimeout(autoHideTimeoutRef.current);
      }
    };
  }, []);

  const connectToStream = () => {
    try {
      // Close existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Create new EventSource connection
      const eventSource = new EventSource('http://localhost:5000/api/streaming/llm-events');
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('🔗 LLM Streaming connected');
        setIsConnected(true);
        setConnectionError(null);
      };

      eventSource.onerror = (error) => {
        console.error('❌ LLM Streaming error:', error);
        setIsConnected(false);
        setConnectionError('Connection lost');
        
        // Attempt to reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          connectToStream();
        }, 5000);
      };

      // Handle different event types
      eventSource.addEventListener('connected', (event) => {
        const data = JSON.parse(event.data);
        console.log('✅ Connected:', data.message);
      });

      eventSource.addEventListener('queue_status', (event) => {
        const data = JSON.parse(event.data);
        setQueueStatus(data);
        setLastActivity(new Date());
      });

      eventSource.addEventListener('generation_started', (event) => {
        const data = JSON.parse(event.data);
        setCurrentGeneration({
          ...data.item,
          status: 'generating',
          partial_text: ''
        });
        setIsMinimized(false); // Auto-expand when generation starts
        setLastActivity(new Date());
        clearAutoHideTimeout();
      });

      eventSource.addEventListener('generation_update', (event) => {
        const data = JSON.parse(event.data);
        setCurrentGeneration(prev => ({
          ...prev,
          partial_text: data.partial_text
        }));
        setLastActivity(new Date());
      });

      eventSource.addEventListener('generation_completed', (event) => {
        const data = JSON.parse(event.data);
        setCurrentGeneration({
          ...data.item,
          status: 'completed'
        });
        setLastActivity(new Date());
        startAutoHideTimer();
      });

      eventSource.addEventListener('generation_failed', (event) => {
        const data = JSON.parse(event.data);
        setCurrentGeneration({
          ...data.item,
          status: 'failed'
        });
        setLastActivity(new Date());
        startAutoHideTimer();
      });

      eventSource.addEventListener('queue_update', (event) => {
        const data = JSON.parse(event.data);
        // Update queue status based on action
        setLastActivity(new Date());
      });

      eventSource.addEventListener('ping', (event) => {
        // Keep-alive ping - just update last activity
        setLastActivity(new Date());
      });

    } catch (error) {
      console.error('❌ Failed to connect to streaming:', error);
      setConnectionError(error.message);
    }
  };

  const startAutoHideTimer = () => {
    clearAutoHideTimeout();
    autoHideTimeoutRef.current = setTimeout(() => {
      setIsMinimized(true);
    }, 10000); // Auto-minimize after 10 seconds of completion
  };

  const clearAutoHideTimeout = () => {
    if (autoHideTimeoutRef.current) {
      clearTimeout(autoHideTimeoutRef.current);
      autoHideTimeoutRef.current = null;
    }
  };

  const toggleMinimized = () => {
    setIsMinimized(!isMinimized);
    clearAutoHideTimeout();
  };

  const getStatusColor = () => {
    if (!isConnected) return '#e74c3c';
    if (currentGeneration?.status === 'generating') return '#f39c12';
    if (currentGeneration?.status === 'completed') return '#27ae60';
    if (currentGeneration?.status === 'failed') return '#e74c3c';
    return '#6c757d';
  };

// Timing Calculation Fix
// Replace the formatDuration function in frontend/src/components/streaming/StreamingDisplay.js

  const formatDuration = (item) => {
    if (!item.started_at) return 'Not started';
  
    try {
      const start = new Date(item.started_at);
      const end = item.completed_at ? new Date(item.completed_at) : new Date();
    
      // Check if dates are valid
      if (isNaN(start.getTime()) || isNaN(end.getTime())) {
        return 'Invalid time';
      }
    
      const duration = (end - start) / 1000;
    
      // Sanity check - if duration is unreasonable, show a fallback
      if (duration < 0 || duration > 3600) { // More than 1 hour seems wrong
        return 'Calculating...';
      }
    
      return `${duration.toFixed(1)}s`;
    } catch (error) {
      console.error('Duration calculation error:', error);
      return 'Error';
    }
  };

  // Don't render if never connected and no activity
  if (!isConnected && !currentGeneration && !lastActivity) {
    return null;
  }

  return (
    <div className={`streaming-display ${isMinimized ? 'minimized' : 'expanded'}`}>
      {/* Header Bar */}
      <div className="streaming-header" onClick={toggleMinimized}>
        <div className="streaming-status">
          <div 
            className="status-indicator"
            style={{ backgroundColor: getStatusColor() }}
          />
          <span className="status-text">
            {!isConnected ? 'Disconnected' : 
             currentGeneration?.status === 'generating' ? 'Generating...' :
             currentGeneration?.status === 'completed' ? 'Completed' :
             currentGeneration?.status === 'failed' ? 'Failed' :
             'Ready'}
          </span>
        </div>
        
        <div className="streaming-controls">
          {queueStatus && (
            <span className="queue-count">
              Queue: {queueStatus.queue_size}
            </span>
          )}
          <button className="minimize-button">
            {isMinimized ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {!isMinimized && (
        <div className="streaming-content">
          {connectionError && (
            <div className="connection-error">
              ❌ {connectionError}
            </div>
          )}

          {currentGeneration && (
            <div className="current-generation">
              <div className="generation-header">
                <span className="generation-type">
                  {currentGeneration.prompt_type}
                </span>
                <span className="generation-duration">
                  {formatDuration(currentGeneration)}
                </span>
              </div>
              
              {currentGeneration.status === 'generating' && (
                <div className="generation-progress">
                  <div className="progress-bar">
                    <div className="progress-fill" />
                  </div>
                  <div className="progress-text">
                    Generating response...
                  </div>
                </div>
              )}

              <div className="generation-output">
                {currentGeneration.partial_text ? (
                  <div className="partial-text">
                    {currentGeneration.partial_text}
                    {currentGeneration.status === 'generating' && (
                      <span className="cursor">|</span>
                    )}
                  </div>
                ) : (
                  <div className="no-output">
                    {currentGeneration.status === 'generating' ? 
                      'Waiting for response...' : 
                      'No output available'}
                  </div>
                )}
              </div>

              {currentGeneration.error && (
                <div className="generation-error">
                  ❌ {currentGeneration.error}
                </div>
              )}
            </div>
          )}

          {queueStatus && (
            <div className="queue-summary">
              <div className="queue-stats">
                <span>Total: {queueStatus.total_items}</span>
                <span>Pending: {queueStatus.status_counts?.pending || 0}</span>
                <span>Completed: {queueStatus.status_counts?.completed || 0}</span>
                <span>Failed: {queueStatus.status_counts?.failed || 0}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default StreamingDisplay;