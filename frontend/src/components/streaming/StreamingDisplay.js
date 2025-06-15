// Streaming Display Component - IMPROVED
// Always-visible overlay showing real-time LLM generation progress
// Now with token-level updates and auto-scroll functionality

import React, { useState, useEffect, useRef } from 'react';

function StreamingDisplay() {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [currentGeneration, setCurrentGeneration] = useState(null);
  const [queueStatus, setQueueStatus] = useState(null);
  const [isMinimized, setIsMinimized] = useState(false);
  const [lastActivity, setLastActivity] = useState(null);
  const [streamingText, setStreamingText] = useState('');
  
  // Refs for auto-scroll functionality
  const outputRef = useRef(null);
  const eventSourceRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const autoHideTimeoutRef = useRef(null);
  const lastTextLengthRef = useRef(0);

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

  // Auto-scroll effect - triggers when streamingText changes
  useEffect(() => {
    if (outputRef.current && streamingText && currentGeneration?.status === 'generating') {
      const outputElement = outputRef.current;
      const newTextLength = streamingText.length;
      
      // Only auto-scroll if text has actually grown (new tokens)
      if (newTextLength > lastTextLengthRef.current) {
        // Check if user has manually scrolled up
        const isScrolledToBottom = outputElement.scrollHeight - outputElement.clientHeight <= outputElement.scrollTop + 1;
        const isNearBottom = outputElement.scrollHeight - outputElement.clientHeight <= outputElement.scrollTop + 50;
        
        // Auto-scroll if user hasn't manually scrolled up
        if (isScrolledToBottom || isNearBottom) {
          outputElement.scrollTop = outputElement.scrollHeight;
        }
        
        lastTextLengthRef.current = newTextLength;
      }
    }
  }, [streamingText, currentGeneration?.status]);

  const connectToStream = () => {
    try {
      // Close existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      console.log('🔗 Connecting to LLM streaming...');
      
      // Create new EventSource connection
      const eventSource = new EventSource('http://localhost:5000/api/streaming/llm-events');
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('✅ LLM Streaming connected');
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
        console.log('✅ SSE Connected:', data.message);
      });

      eventSource.addEventListener('queue_status', (event) => {
        const data = JSON.parse(event.data);
        console.log('📊 Queue status:', data);
        setQueueStatus(data);
        setLastActivity(new Date());
      });

      eventSource.addEventListener('generation_started', (event) => {
        const data = JSON.parse(event.data);
        console.log('🎲 Generation started:', data);
        
        setCurrentGeneration({
          ...data.item,
          status: 'generating',
          request_id: data.request_id
        });
        setStreamingText(''); // Reset streaming text
        lastTextLengthRef.current = 0; // Reset length tracker
        setIsMinimized(false); // Auto-expand when generation starts
        setLastActivity(new Date());
        clearAutoHideTimeout();
      });

      eventSource.addEventListener('generation_update', (event) => {
        const data = JSON.parse(event.data);
        
        // More frequent logging for token-level updates
        if (data.partial_text !== undefined) {
          const tokenCount = data.partial_text.split(' ').length;
          console.log(`📝 Token update: ${tokenCount} tokens, ${data.partial_text.length} chars`);
          
          // Update streaming text immediately
          setStreamingText(data.partial_text);
        }
        
        setCurrentGeneration(prev => ({
          ...prev,
          partial_text: data.partial_text,
          tokens_so_far: data.tokens_so_far
        }));
        setLastActivity(new Date());
      });

      eventSource.addEventListener('generation_completed', (event) => {
        const data = JSON.parse(event.data);
        console.log('✅ Generation completed:', {
          tokens: data.tokens_generated,
          duration: data.duration,
          final_text_length: data.final_text?.length || 0
        });
        
        setCurrentGeneration({
          ...data.item,
          status: 'completed',
          final_text: data.final_text,
          tokens_generated: data.tokens_generated,
          duration: data.duration
        });
        setStreamingText(data.final_text || '');
        setLastActivity(new Date());
        startAutoHideTimer();
      });

      eventSource.addEventListener('generation_failed', (event) => {
        const data = JSON.parse(event.data);
        console.log('❌ Generation failed:', data.error);
        
        setCurrentGeneration({
          ...data.item,
          status: 'failed',
          error: data.error
        });
        setLastActivity(new Date());
        startAutoHideTimer();
      });

      eventSource.addEventListener('queue_update', (event) => {
        const data = JSON.parse(event.data);
        console.log('📥 Queue update:', data.action);
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
    }, 15000); // Auto-minimize after 15 seconds of completion
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
                    {currentGeneration.tokens_so_far ? 
                      `Generated ${currentGeneration.tokens_so_far} tokens...` : 
                      'Generating response...'}
                  </div>
                </div>
              )}

              {/* IMPROVED: Auto-scrolling output with ref */}
              <div className="generation-output" ref={outputRef}>
                {streamingText ? (
                  <div className="partial-text">
                    {streamingText}
                    {currentGeneration.status === 'generating' && (
                      <span className="cursor">|</span>
                    )}
                  </div>
                ) : currentGeneration.status === 'generating' ? (
                  <div className="no-output">
                    <div className="loading-dots">
                      Waiting for response<span className="dots">...</span>
                    </div>
                  </div>
                ) : currentGeneration.status === 'completed' ? (
                  <div className="completion-summary">
                    ✅ Generated {currentGeneration.tokens_generated || 0} tokens 
                    {currentGeneration.duration && ` in ${currentGeneration.duration.toFixed(1)}s`}
                  </div>
                ) : (
                  <div className="no-output">
                    No output available
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

          {/* Debug info for development */}
          {process.env.NODE_ENV === 'development' && currentGeneration && (
            <div className="debug-info">
              <details>
                <summary>🐛 Debug Info</summary>
                <pre style={{fontSize: '10px', overflow: 'auto', maxHeight: '100px'}}>
                  {JSON.stringify({
                    status: currentGeneration.status,
                    request_id: currentGeneration.request_id,
                    streaming_text_length: streamingText?.length || 0,
                    tokens_so_far: currentGeneration.tokens_so_far,
                    last_activity: lastActivity?.toISOString(),
                    auto_scroll_active: currentGeneration.status === 'generating'
                  }, null, 2)}
                </pre>
              </details>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default StreamingDisplay;