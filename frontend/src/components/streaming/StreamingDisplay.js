// StreamingDisplay Component - REVERTED TO ORIGINAL + DEBUG SECTION
// Back to the simple version with added expandable debug info section
// Shows raw streaming context data for development and debugging

import React, { useState, useRef, useEffect } from 'react';
import { StatusBadge, Button, Alert } from '../../shared/ui/index.js';
import { useStreaming } from '../../app/contexts/streamingContext/useStreamingContext.js';
import './streaming.css';

function StreamingDisplay() {
  
  // Get raw streaming state from context
  const streamingState = useStreaming();
  
  // Destructure the core streaming data (same as original)
  const {
    isConnected,
    connectionError,
    currentGeneration,
    streamingText,
    lastActivity
  } = streamingState;

  // UI state managed locally (moved from provider)
  const [isMinimized, setIsMinimized] = useState(false);
  const [isDebugExpanded, setIsDebugExpanded] = useState(false);
  
  // Auto-scroll ref
  const outputRef = useRef(null);

  // Derived state
  const isGenerating = currentGeneration?.status === 'generating';

  // Auto-expand when generation starts
  useEffect(() => {
    if (isGenerating) {
      setIsMinimized(false);
    }
  }, [isGenerating]);

  // Auto-scroll when text updates
  useEffect(() => {
    if (outputRef.current && streamingText && isGenerating) {
      const outputElement = outputRef.current;
      outputElement.scrollTop = outputElement.scrollHeight;
    }
  }, [streamingText, isGenerating]);

  // Don't render if no activity
  if (!isConnected && !currentGeneration && !lastActivity) {
    return null;
  }

  const getStatusText = () => {
    if (!isConnected) return 'Disconnected';
    if (isGenerating) return 'Generating...';
    if (currentGeneration?.status === 'completed') return 'Completed';
    if (currentGeneration?.status === 'failed') return 'Failed';
    return 'Ready';
  };

  // Prepare debug data (clean version for display)
  const debugData = {
    // Connection info
    connection: {
      isConnected,
      connectionError,
      lastActivity: lastActivity?.toISOString() || null
    },
    
    // Current generation
    currentGeneration: currentGeneration ? {
      ...currentGeneration,
      // Convert dates to strings for JSON display
      startedAt: currentGeneration.startedAt || null,
      completedAt: currentGeneration.completedAt || null
    } : null,
    
    // Text data
    streaming: {
      textLength: streamingText?.length || 0,
      hasText: !!streamingText,
      isGenerating
    },

    // All raw state (truncated for readability)
    rawState: {
      ...streamingState,
      streamingText: streamingText ? `${streamingText.substring(0, 100)}...` : null,
      lastActivity: lastActivity?.toISOString() || null
    }
  };

  return (
    <div className={`streaming-display ${isMinimized ? 'minimized' : 'expanded'}`}>
      
      {/* Header */}
      <div className="streaming-header" onClick={() => setIsMinimized(!isMinimized)}>
        <div className="streaming-status">
          <span>{getStatusText()}</span>
        </div>
        
        <Button variant="ghost" size="sm">
          {isMinimized ? '▲' : '▼'}
        </Button>
      </div>

      {/* Content (only when expanded) */}
      {!isMinimized && (
        <div className="streaming-content">
          
          {/* Error */}
          {connectionError && (
            <Alert type="error" size="sm">
              {connectionError}
            </Alert>
          )}

          {/* Generation Output */}
          {currentGeneration && (
            <div className="streaming-generation">
              <div className="generation-info">
                <span>{currentGeneration.promptType || 'Generation'}</span>
                {isGenerating && currentGeneration.tokensSoFar && (
                  <span>{currentGeneration.tokensSoFar} tokens</span>
                )}
              </div>
              
              <div ref={outputRef} className="streaming-output">
                {streamingText ? (
                  <div>
                    {streamingText}
                    {isGenerating && <span className="cursor">|</span>}
                  </div>
                ) : isGenerating ? (
                  <div>Generating...</div>
                ) : (
                  <div>No output</div>
                )}
              </div>
            </div>
          )}

          {/* Debug Info Section */}
          <div className="debug-section">
            <div 
              className="debug-header" 
              onClick={() => setIsDebugExpanded(!isDebugExpanded)}
            >
              <span className="debug-title">🐛 Debug Info</span>
              <Button variant="ghost" size="sm">
                {isDebugExpanded ? '▼' : '▶'}
              </Button>
            </div>

            {isDebugExpanded && (
              <div className="debug-content">
                <div className="debug-summary">
                  <div className="debug-stat">
                    <span className="debug-label">Connected:</span>
                    <span className="debug-value">{isConnected ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="debug-stat">
                    <span className="debug-label">Generating:</span>
                    <span className="debug-value">{isGenerating ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="debug-stat">
                    <span className="debug-label">Text Length:</span>
                    <span className="debug-value">{streamingText?.length || 0}</span>
                  </div>
                  {lastActivity && (
                    <div className="debug-stat">
                      <span className="debug-label">Last Activity:</span>
                      <span className="debug-value">{lastActivity.toLocaleTimeString()}</span>
                    </div>
                  )}
                </div>

                <div className="debug-raw-data">
                  <div className="debug-subsection">
                    <h5>Raw Streaming State:</h5>
                    <pre className="debug-json">
                      {JSON.stringify(debugData, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}

export default StreamingDisplay;