// StreamingDisplay Component - Clean rewrite with Card and CardSection structure
// Real-time AI generation monitoring with collapsible sections
// Uses shared UI components for consistent styling and behavior

import React, { useState } from 'react';
import { Badge, Button, Card, CardSection } from '../../shared/ui/index.js';
import { Table } from '../../shared/ui/Table/index.js';
import { Scroll } from '../../shared/ui/Scroll/index.js';
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
    imageGenerationStarted,
    imageGenerationUpdate,
    imageGenerationCompleted,
    imageGenerationFailed,
    AiQueueUpdate,
    lastActivity,
    activeGeneration,
    currentActivity
  } = streamingState;

  // UI state for collapsible sections and main card
  const [isMinimized, setIsMinimized] = useState(false);
  const [collapsedSections, setCollapsedSections] = useState({
    activeGeneration: false,
    queueStatus: false,
    llmGeneration: false,
    imageGeneration: false
  });

  // Toggle section collapse
  const toggleSection = (sectionName) => {
    setCollapsedSections(prev => ({
      ...prev,
      [sectionName]: !prev[sectionName]
    }));
  };

  // Helper functions
  const formatTime = (timestamp) => {
    if (!timestamp) return '--';
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '--';
    return `${seconds.toFixed(2)}s`;
  };

  // Get status variant for badges
  const getStatusVariant = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'generating': 
      case 'processing': return 'info';
      case 'failed': return 'error';
      default: return 'secondary';
    }
  };

  return (
    <div className="streaming-display">
      
      {/* Header - Always visible with activity status */}
      <div 
        className="streaming-header"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="streaming-status">
          <span className="streaming-title">🔄 Streaming Monitor</span>
          
          {/* Activity Badge */}
          {currentActivity?.type ? (
            <Badge variant="info">
              {`${currentActivity.label}: ${currentActivity.progress}`}
            </Badge>
          ) : currentActivity?.label === 'Idle' ? (
            <Badge variant="secondary">🟢 Idle</Badge>
          ) : isConnected ? (
            <Badge variant="success">🟢 Connected</Badge>
          ) : (
            <Badge variant="error">🔴 Disconnected</Badge>
          )}
        </div>
        
        <Button 
          variant="ghost" 
          size="sm"
          aria-label={isMinimized ? 'Expand' : 'Minimize'}
        >
          {isMinimized ? '▶' : '▼'}
        </Button>
      </div>

      {/* Scrollable Card Content - hidden when minimized */}
      {!isMinimized && (
        <Card 
          size="md" 
          variant="elevated"
          className="streaming-card-content"
        >
            
            {/* 🚀 Active Generation Section */}
            {activeGeneration.queueItem && (
              <CardSection 
                type="content"
                title="🚀 Active Generation"
                action={
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => toggleSection('activeGeneration')}
                  >
                    {collapsedSections.activeGeneration ? '▶' : '▼'}
                  </Button>
                }
              >
                {!collapsedSections.activeGeneration && (
                  <Table
                    columns={[
                      { key: 'generationId', header: 'ID', width: '15%' },
                      { key: 'generationType', header: 'Type', width: '12%' },
                      { key: 'promptType', header: 'Prompt Type', width: '25%' },
                      { key: 'promptName', header: 'Prompt Name', width: '33%' },
                      { key: 'status', header: 'Status', width: '15%',
                        render: (status) => (
                          <Badge variant={getStatusVariant(status)}>
                            {status}
                          </Badge>
                        )
                      }
                    ]}
                    data={[{
                      ...activeGeneration.queueItem,
                      status: activeGeneration.state
                    }]}
                    size="sm"
                    striped
                  />
                )}
              </CardSection>
            )}

            {/* 📋 Queue Status Section */}
            <CardSection 
              type="content"
              title={`📋 Queue Status (${AiQueueUpdate?.allAiQueueItems?.length || 0} items)`}
              action={
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => toggleSection('queueStatus')}
                >
                  {collapsedSections.queueStatus ? '▶' : '▼'}
                </Button>
              }
            >
              {!collapsedSections.queueStatus && (
                <>
                  {AiQueueUpdate?.allAiQueueItems?.length > 0 ? (
                    <Table
                      columns={[
                        { key: 'generationId', header: 'ID', width: '12%' },
                        { key: 'generationType', header: 'Type', width: '10%' },
                        { key: 'promptType', header: 'Prompt Type', width: '20%' },
                        { key: 'promptName', header: 'Prompt Name', width: '22%' },
                        { key: 'priority', header: 'Priority', width: '10%' },
                        { key: 'createdAt', header: 'Created', width: '14%',
                          render: (timestamp) => formatTime(timestamp)
                        },
                        { key: 'status', header: 'Status', width: '12%',
                          render: (status) => (
                            <Badge variant={getStatusVariant(status)}>
                              {status}
                            </Badge>
                          )
                        }
                      ]}
                      data={AiQueueUpdate.allAiQueueItems}
                      size="sm"
                      striped
                      hover
                    />
                  ) : (
                    <div className="empty-queue">
                      <p>✅ Queue is empty</p>
                      {AiQueueUpdate?.trigger && (
                        <p className="queue-trigger">Last trigger: {AiQueueUpdate.trigger}</p>
                      )}
                    </div>
                  )}
                </>
              )}
            </CardSection>

            {/* 🤖 LLM Generation Section */}
            {(llmGenerationStarted || llmGenerationUpdate || llmGenerationCompleted || llmGenerationFailed) && (
              <CardSection 
                type="content"
                title="🤖 LLM Generation"
                action={
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => toggleSection('llmGeneration')}
                  >
                    {collapsedSections.llmGeneration ? '▶' : '▼'}
                  </Button>
                }
              >
                {!collapsedSections.llmGeneration && (
                  <>
                    
                    {/* Streaming Text Display - Primary Focus */}
                    {(llmGenerationUpdate?.partialText || llmGenerationCompleted?.result?.text) && (
                      <div className="streaming-text-section">
                        <h4>📝 Streaming Text</h4>
                        <Scroll 
                          maxHeight="200px" 
                          className="scroll-streaming"
                        >
                          {llmGenerationUpdate?.partialText || llmGenerationCompleted?.result?.text}
                          {llmGenerationUpdate?.partialText && !llmGenerationCompleted && (
                            <span className="cursor">|</span>
                          )}
                        </Scroll>
                      </div>
                    )}

                    {/* LLM Completion Results */}
                    {llmGenerationCompleted && (
                      <div className="completion-section">
                        <h4>✅ Generation Completed</h4>
                        <Table
                          columns={[
                            { key: 'generationId', header: 'ID', width: '12%' },
                            { key: 'promptType', header: 'Prompt Type', width: '20%' },
                            { key: 'promptName', header: 'Prompt Name', width: '20%' },
                            { key: 'tokens', header: 'Tokens', width: '8%' },
                            { key: 'duration', header: 'Duration', width: '10%' },
                            { key: 'tokensPerSecond', header: 'Tokens/Sec', width: '10%' },
                            { key: 'attempt', header: 'Attempt', width: '8%' },
                            { key: 'parsingSuccess', header: 'Parsing', width: '12%',
                              render: (success) => success ? '✅' : '❌'
                            }
                          ]}
                          data={[{
                            generationId: llmGenerationCompleted.aiQueueItem?.generationId,
                            promptType: llmGenerationCompleted.aiQueueItem?.promptType,
                            promptName: llmGenerationCompleted.aiQueueItem?.promptName,
                            tokens: llmGenerationCompleted.result?.tokens,
                            duration: formatDuration(llmGenerationCompleted.result?.duration),
                            tokensPerSecond: llmGenerationCompleted.result?.tokensPerSecond,
                            attempt: llmGenerationCompleted.result?.attempt,
                            parsingSuccess: llmGenerationCompleted.result?.parsingSuccess
                          }]}
                          size="sm"
                          striped
                        />

                        {/* Generated Game Content */}
                        {llmGenerationCompleted.result?.parsedData && (
                          <div className="game-content-section">
                            <h4>🎮 Generated Game Content</h4>
                            <Scroll 
                              maxHeight="150px"
                              className="scroll-code"
                            >
                              {JSON.stringify(llmGenerationCompleted.result.parsedData, null, 2)}
                            </Scroll>
                          </div>
                        )}

                        {/* Parsing Error */}
                        {llmGenerationCompleted.result?.parsingError && (
                          <div className="parsing-error">
                            <h4>⚠️ Parsing Error</h4>
                            <div className="error-text">
                              {llmGenerationCompleted.result.parsingError}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* LLM Error */}
                    {llmGenerationFailed && (
                      <div className="error-section">
                        <h4>❌ LLM Generation Failed</h4>
                        <div className="error-text">
                          {llmGenerationFailed.error}
                        </div>
                      </div>
                    )}
                    
                  </>
                )}
              </CardSection>
            )}

            {/* 🎨 Image Generation Section */}
            {(imageGenerationStarted || imageGenerationUpdate || imageGenerationCompleted || imageGenerationFailed) && (
              <CardSection 
                type="content"
                title="🎨 Image Generation"
                action={
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => toggleSection('imageGeneration')}
                  >
                    {collapsedSections.imageGeneration ? '▶' : '▼'}
                  </Button>
                }
              >
                {!collapsedSections.imageGeneration && (
                  <>
                    
                    {/* Image Generation Progress */}
                    {imageGenerationUpdate && !imageGenerationCompleted && (
                      <div className="image-progress">
                        <p>🔄 Processing... ({imageGenerationUpdate.elapsedSeconds}s elapsed)</p>
                      </div>
                    )}

                    {/* Image Completion Results */}
                    {imageGenerationCompleted && (
                      <div className="completion-section">
                        <h4>✅ Image Generated</h4>
                        <Table
                          columns={[
                            { key: 'generationId', header: 'ID', width: '15%' },
                            { key: 'promptType', header: 'Prompt Type', width: '25%' },
                            { key: 'promptName', header: 'Prompt Name', width: '25%' },
                            { key: 'imagePath', header: 'Image Path', width: '20%' },
                            { key: 'executionTime', header: 'Execution Time', width: '15%' }
                          ]}
                          data={[{
                            generationId: imageGenerationCompleted.aiQueueItem?.generationId,
                            promptType: imageGenerationCompleted.aiQueueItem?.promptType,
                            promptName: imageGenerationCompleted.aiQueueItem?.promptName,
                            imagePath: imageGenerationCompleted.result?.imagePath,
                            executionTime: formatDuration(imageGenerationCompleted.result?.executionTime)
                          }]}
                          size="sm"
                          striped
                        />

                        {/* Generated Image Display */}
                        {imageGenerationCompleted.result?.imagePath && (
                          <div className="image-display">
                            <h4>🖼️ Generated Image</h4>
                            <div className="image-container">
                              <img 
                                src={`http://localhost:5000/api/monsters/card-art/${imageGenerationCompleted.result.imagePath}`}
                                alt="Generated monster card art"
                                className="generated-image"
                                onError={(e) => {
                                  console.error('Failed to load image:', e.target.src);
                                  e.target.style.display = 'none';
                                }}
                              />
                              <div className="image-meta">
                                <p><strong>Dimensions:</strong> {imageGenerationCompleted.result?.imageDimensions}</p>
                                <p><strong>Workflow:</strong> {imageGenerationCompleted.result?.workflowUsed}</p>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Image Error */}
                    {imageGenerationFailed && (
                      <div className="error-section">
                        <h4>❌ Image Generation Failed</h4>
                        <div className="error-text">
                          {imageGenerationFailed.error}
                        </div>
                      </div>
                    )}
                    
                  </>
                )}
              </CardSection>
            )}

        </Card>
      )}
    </div>
  );
}

export default StreamingDisplay;