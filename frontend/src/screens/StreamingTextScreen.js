// StreamingTestScreen - Simple test to verify streaming context works
// Shows all streaming data and connection controls

import React from 'react';
import { Button, StatusBadge, Alert } from '../shared/ui/index.js';
import { useStreaming } from '../app/contexts/streamingContext/useStreamingContext.js';

function StreamingTestScreen() {
  
  // Get all streaming data from context
  const { 
    isConnected,
    connectionError,
    currentGeneration,
    streamingText,
    queueStatus,
    lastActivity,
    isGenerating,
    hasActiveGeneration,
    connect,
    disconnect
  } = useStreaming();

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      
      {/* Header */}
      <h1>🧪 Streaming Context Test</h1>
      <p>Testing the streaming context and EventSource connection</p>

      {/* Connection Controls */}
      <div style={{ 
        display: 'flex', 
        gap: '1rem', 
        alignItems: 'center',
        marginBottom: '2rem',
        padding: '1rem',
        border: '1px solid var(--color-border)',
        borderRadius: '8px'
      }}>
        <StatusBadge 
          status={isConnected ? 'success' : 'error'} 
          size="md" 
        />
        <span>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
        
        <Button 
          variant="primary" 
          size="sm" 
          onClick={connect}
          disabled={isConnected}
        >
          Connect
        </Button>
        
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={disconnect}
          disabled={!isConnected}
        >
          Disconnect
        </Button>
      </div>

      {/* Connection Error */}
      {connectionError && (
        <Alert type="error" style={{ marginBottom: '1rem' }}>
          {connectionError}
        </Alert>
      )}

      {/* Current State */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        
        {/* Connection Info */}
        <div style={{ 
          padding: '1rem',
          border: '1px solid var(--color-border)',
          borderRadius: '8px'
        }}>
          <h3>Connection Status</h3>
          <p><strong>Connected:</strong> {isConnected ? 'Yes' : 'No'}</p>
          <p><strong>Last Activity:</strong> {lastActivity ? lastActivity.toLocaleTimeString() : 'None'}</p>
          <p><strong>Is Generating:</strong> {isGenerating ? 'Yes' : 'No'}</p>
          <p><strong>Has Active Generation:</strong> {hasActiveGeneration ? 'Yes' : 'No'}</p>
        </div>

        {/* Queue Status */}
        <div style={{ 
          padding: '1rem',
          border: '1px solid var(--color-border)',
          borderRadius: '8px'
        }}>
          <h3>Queue Status</h3>
          {queueStatus ? (
            <>
              <p><strong>Queue Size:</strong> {queueStatus.queueSize}</p>
              <p><strong>Total Items:</strong> {queueStatus.totalItems}</p>
              <p><strong>Pending:</strong> {queueStatus.statusCounts?.pending || 0}</p>
              <p><strong>Completed:</strong> {queueStatus.statusCounts?.completed || 0}</p>
              <p><strong>Failed:</strong> {queueStatus.statusCounts?.failed || 0}</p>
            </>
          ) : (
            <p>No queue data</p>
          )}
        </div>
      </div>

      {/* Current Generation */}
      {currentGeneration && (
        <div style={{ 
          padding: '1rem',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          marginBottom: '1rem'
        }}>
          <h3>Current Generation</h3>
          <p><strong>ID:</strong> {currentGeneration.id}</p>
          <p><strong>Status:</strong> {currentGeneration.status}</p>
          <p><strong>Prompt Type:</strong> {currentGeneration.promptType}</p>
          <p><strong>Request ID:</strong> {currentGeneration.requestId}</p>
          <p><strong>Started At:</strong> {currentGeneration.startedAt}</p>
          {currentGeneration.tokensSoFar && (
            <p><strong>Tokens So Far:</strong> {currentGeneration.tokensSoFar}</p>
          )}
          {currentGeneration.tokensGenerated && (
            <p><strong>Tokens Generated:</strong> {currentGeneration.tokensGenerated}</p>
          )}
          {currentGeneration.duration && (
            <p><strong>Duration:</strong> {currentGeneration.duration}s</p>
          )}
          {currentGeneration.error && (
            <p><strong>Error:</strong> {currentGeneration.error}</p>
          )}
        </div>
      )}

      {/* Streaming Text */}
      {streamingText && (
        <div style={{ 
          padding: '1rem',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          backgroundColor: 'var(--color-background-secondary)'
        }}>
          <h3>Streaming Text ({streamingText.length} characters)</h3>
          <div style={{
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            lineHeight: '1.5',
            maxHeight: '200px',
            overflowY: 'auto',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word'
          }}>
            {streamingText}
            {isGenerating && <span style={{ animation: 'blink 1s infinite' }}>|</span>}
          </div>
        </div>
      )}

      {/* Raw Debug Info */}
      <details style={{ marginTop: '2rem' }}>
        <summary>🐛 Raw Debug Data</summary>
        <pre style={{
          fontSize: '0.75rem',
          background: 'var(--color-background-secondary)',
          padding: '1rem',
          borderRadius: '4px',
          overflow: 'auto',
          maxHeight: '300px'
        }}>
          {JSON.stringify({
            isConnected,
            connectionError,
            currentGeneration,
            streamingText: streamingText ? `${streamingText.substring(0, 100)}...` : null,
            queueStatus,
            lastActivity: lastActivity?.toISOString(),
            isGenerating,
            hasActiveGeneration
          }, null, 2)}
        </pre>
      </details>

      <style jsx>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}

export default StreamingTestScreen;