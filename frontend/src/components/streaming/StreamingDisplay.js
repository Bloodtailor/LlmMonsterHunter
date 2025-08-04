// StreamingDisplay Component - Conservative approach using only known fields
// Only uses the exact fields from the EventSchema definitions provided
// Everything else goes in debug info for discovery

import React, { useState, useRef, useEffect } from 'react';
import { StatusBadge, Button, Alert } from '../../shared/ui/index.js';
import { useStreaming } from '../../app/contexts/streamingContext/useStreamingContext.js';
import './streaming.css';

function StreamingDisplay() {
  
  // Get streaming state from context
  const streamingState = useStreaming();
  
  // Destructure the event-based state structure
  const {
    isConnected,
    connectionError,
    llmGenerationStarted,
    llmGenerationUpdate,
    llmGenerationCompleted,
    llmGenerationFailed,
    llmQueueUpdate,
    imageGenerationStarted,
    imageGenerationUpdate,
    imageGenerationCompleted,
    imageGenerationFailed,
    imageQueueUpdate,
    lastActivity
  } = streamingState;

  // UI state managed locally
  const [isMinimized, setIsMinimized] = useState(false);
  const [isDebugExpanded, setIsDebugExpanded] = useState(false);
  
  // Auto-scroll ref
  const outputRef = useRef(null);

  // Only use fields I know exist for certain
  const llmGenerationId = llmGenerationStarted?.generationId || null;
  const streamingText = llmGenerationUpdate?.partialText || '';
  const tokenCount = llmGenerationUpdate?.tokensSoFar || null;
  const llmError = llmGenerationFailed?.error || null;
  const llmQueueSize = llmQueueUpdate?.queueSize || null;
  
  const imageGenerationId = imageGenerationStarted?.generationId || null;
  const imageError = imageGenerationFailed?.error || null;
  const imageQueueSize = imageQueueUpdate?.queueSize || null;

  // Simple derived state
  const hasLlmGeneration = !!llmGenerationId;
  const hasImageGeneration = !!imageGenerationId;
  const isLlmGenerating = hasLlmGeneration && !llmGenerationCompleted && !llmGenerationFailed;
  const isImageGenerating = hasImageGeneration && !imageGenerationCompleted && !imageGenerationFailed;

  // Auto-expand when generation starts
  useEffect(() => {
    if (isLlmGenerating || isImageGenerating) {
      setIsMinimized(false);
    }
  }, [isLlmGenerating, isImageGenerating]);

  // Auto-scroll when text updates
  useEffect(() => {
    if (outputRef.current && streamingText && isLlmGenerating) {
      const outputElement = outputRef.current;
      outputElement.scrollTop = outputElement.scrollHeight;
    }
  }, [streamingText, isLlmGenerating]);

  // Don't render if no activity
  if (!isConnected && !hasLlmGeneration && !hasImageGeneration && !lastActivity) {
    return null;
  }

  const getStatusText = () => {
    if (!isConnected) return 'Disconnected';
    if (isLlmGenerating) return 'Generating LLM...';
    if (isImageGenerating) return 'Generating Image...';
    if (llmGenerationCompleted) return 'LLM Completed';
    if (imageGenerationCompleted) return 'Image Completed';
    if (llmError) return 'LLM Failed';
    if (imageError) return 'Image Failed';
    return 'Ready';
  };

  return (
    <div className={`streaming-display ${isMinimized ? 'minimized' : 'expanded'}`}>
      
      {/* Header */}
      <div className="streaming-header" onClick={() => setIsMinimized(!isMinimized)}>
        <div className="streaming-status">
          <span>{getStatusText()}</span>
          {(isLlmGenerating || isImageGenerating) && (
            <StatusBadge status="processing" size="sm" />
          )}
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

          {/* LLM Generation - Only show what I know for certain */}
          {hasLlmGeneration && (
            <div className="streaming-generation">
              <div className="generation-info">
                <span>🤖 LLM Generation</span>
                {llmGenerationId && (
                  <span className="generation-id">ID: {llmGenerationId}</span>
                )}
                {tokenCount && (
                  <span className="tokens">Tokens: {tokenCount}</span>
                )}
              </div>
              
              <div ref={outputRef} className="streaming-output">
                {streamingText ? (
                  <div>
                    {streamingText}
                    {isLlmGenerating && <span className="cursor">|</span>}
                  </div>
                ) : isLlmGenerating ? (
                  <div>Generating...</div>
                ) : llmGenerationCompleted ? (
                  <div>✅ Generation completed</div>
                ) : llmError ? (
                  <div>❌ Error: {llmError}</div>
                ) : (
                  <div>⏳ Started...</div>
                )}
              </div>
            </div>
          )}

          {/* Image Generation - Only show what I know for certain */}
          {hasImageGeneration && (
            <div className="streaming-generation image-generation">
              <div className="generation-info">
                <span>🎨 Image Generation</span>
                {imageGenerationId && (
                  <span className="generation-id">ID: {imageGenerationId}</span>
                )}
              </div>
              
              <div className="image-status">
                {imageGenerationCompleted ? (
                  <div>✅ Image completed</div>
                ) : imageError ? (
                  <div>❌ Error: {imageError}</div>
                ) : imageGenerationUpdate ? (
                  <div>🔄 Processing...</div>
                ) : (
                  <div>⏳ Starting...</div>
                )}
              </div>
            </div>
          )}

          {/* Queue Status - Only show what I know for certain */}
          {(llmQueueSize !== null || imageQueueSize !== null) && (
            <div className="queue-summary">
              <h4>Queue Status</h4>
              {llmQueueSize !== null && (
                <div className="queue-info">
                  <span>🤖 LLM Queue: {llmQueueSize} items</span>
                  {llmQueueUpdate?.action && (
                    <span className="last-action">Last: {llmQueueUpdate.action}</span>
                  )}
                </div>
              )}
              {imageQueueSize !== null && (
                <div className="queue-info">
                  <span>🎨 Image Queue: {imageQueueSize} items</span>
                  {imageQueueUpdate?.action && (
                    <span className="last-action">Last: {imageQueueUpdate.action}</span>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Debug Info Section - Everything unknown goes here */}
          <div className="debug-section">
            <div 
              className="debug-header" 
              onClick={() => setIsDebugExpanded(!isDebugExpanded)}
            >
              <span className="debug-title">🐛 Raw Event Data (for discovery)</span>
              <Button variant="ghost" size="sm">
                {isDebugExpanded ? '▼' : '▶'}
              </Button>
            </div>

            {isDebugExpanded && (
              <div className="debug-content">
                
                {/* Quick Stats */}
                <div className="debug-summary">
                  <div className="debug-stat">
                    <span className="debug-label">Connected:</span>
                    <span className="debug-value">{isConnected ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="debug-stat">
                    <span className="debug-label">LLM Generating:</span>
                    <span className="debug-value">{isLlmGenerating ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="debug-stat">
                    <span className="debug-label">Image Generating:</span>
                    <span className="debug-value">{isImageGenerating ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="debug-stat">
                    <span className="debug-label">Streaming Text Length:</span>
                    <span className="debug-value">{streamingText?.length || 0}</span>
                  </div>
                  {lastActivity && (
                    <div className="debug-stat">
                      <span className="debug-label">Last Activity:</span>
                      <span className="debug-value">{lastActivity.toLocaleTimeString()}</span>
                    </div>
                  )}
                </div>

                {/* LLM Events Raw Data */}
                {(llmGenerationStarted || llmGenerationUpdate || llmGenerationCompleted || llmGenerationFailed || llmQueueUpdate) && (
                  <div className="debug-subsection">
                    <h5>LLM Events (Raw Data):</h5>
                    <pre className="debug-json">
                      {JSON.stringify({
                        started: llmGenerationStarted,
                        update: llmGenerationUpdate,
                        completed: llmGenerationCompleted,
                        failed: llmGenerationFailed,
                        queueUpdate: llmQueueUpdate
                      }, null, 2)}
                    </pre>
                  </div>
                )}

                {/* Image Events Raw Data */}
                {(imageGenerationStarted || imageGenerationUpdate || imageGenerationCompleted || imageGenerationFailed || imageQueueUpdate) && (
                  <div className="debug-subsection">
                    <h5>Image Events (Raw Data):</h5>
                    <pre className="debug-json">
                      {JSON.stringify({
                        started: imageGenerationStarted,
                        update: imageGenerationUpdate,
                        completed: imageGenerationCompleted,
                        failed: imageGenerationFailed,
                        queueUpdate: imageQueueUpdate
                      }, null, 2)}
                    </pre>
                  </div>
                )}

                {/* Complete Raw State */}
                <div className="debug-subsection">
                  <h5>Complete Streaming State:</h5>
                  <pre className="debug-json">
                    {JSON.stringify(streamingState, null, 2)}
                  </pre>
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