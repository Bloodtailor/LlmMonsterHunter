// StreamingDisplay Component - MINIMAL VERSION
// Just the core functionality from original, using your UI primitives

import React, { useRef, useEffect } from 'react';
import { StatusBadge, Button, Alert } from '../../shared/ui/index.js';
import { useStreaming } from '../../app/contexts/streamingContext/useStreamingContext.js';
import './streaming.css';

function StreamingDisplay() {
  
  // Get streaming data from context
  const { 
    currentGeneration, 
    streamingText, 
    isGenerating,
    isConnected, 
    connectionError,
    isMinimized, 
    setIsMinimized,
    lastActivity
  } = useStreaming();

  // Auto-scroll ref
  const outputRef = useRef(null);

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

  // Get status for badge
  const getStatus = () => {
    if (!isConnected) return 'error';
    if (isGenerating) return 'loading';
    return 'success';
  };

  const getStatusText = () => {
    if (!isConnected) return 'Disconnected';
    if (isGenerating) return 'Generating...';
    if (currentGeneration?.status === 'completed') return 'Completed';
    if (currentGeneration?.status === 'failed') return 'Failed';
    return 'Ready';
  };

  return (
    <div className={`streaming-display ${isMinimized ? 'minimized' : 'expanded'}`}>
      
      {/* Header */}
      <div className="streaming-header" onClick={() => setIsMinimized(!isMinimized)}>
        <div className="streaming-status">
          <StatusBadge status={getStatus()} size="md" />
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
        </div>
      )}
    </div>
  );
}

export default StreamingDisplay;