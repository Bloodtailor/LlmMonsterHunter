// StreamingContextDiagnostic Component - Simple debugging display
// Just shows every key in streamingState - no fancy categorization
// This is for debugging, not a pretty UI!

import React, { useState } from 'react';
import { Button, StatusBadge, Alert, Card, CardSection } from '../../shared/ui/index.js';
import { useStreaming } from '../../app/contexts/streamingContext/useStreamingContext.js';
import './streamingContextDiagnostic.css';

function StreamingContextDiagnostic() {
  
  // Get all streaming data from context
  const streamingState = useStreaming();
  
  // Connection controls
  const { connect, disconnect } = streamingState;

  // State for tracking expanded objects and display modes
  const [expandedItems, setExpandedItems] = useState(new Set());
  const [showRawMode, setShowRawMode] = useState(false);

  // Get all keys except functions and sort alphabetically
  const allKeys = Object.keys(streamingState)
    .filter(key => typeof streamingState[key] !== 'function')
    .sort();

  const toggleExpanded = (itemKey) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemKey)) {
      newExpanded.delete(itemKey);
    } else {
      newExpanded.add(itemKey);
    }
    setExpandedItems(newExpanded);
  };

  const expandAll = () => {
    const allExpandableItems = new Set();
    
    const findExpandableItems = (obj, basePath) => {
      if (typeof obj === 'object' && obj !== null) {
        Object.keys(obj).forEach(objKey => {
          const itemPath = `${basePath}.${objKey}`;
          if (typeof obj[objKey] === 'object' && obj[objKey] !== null) {
            allExpandableItems.add(itemPath);
            findExpandableItems(obj[objKey], itemPath);
          }
        });
      }
    };

    allKeys.forEach(key => {
      const value = streamingState[key];
      if (typeof value === 'object' && value !== null) {
        // This matches the path created in renderObjectProperty: parentPath.key
        const rootPath = `${key}.root`;
        allExpandableItems.add(rootPath);
        findExpandableItems(value, rootPath);
      }
    });

    setExpandedItems(allExpandableItems);
  };

  const copyIndividualData = async (key, value) => {
    try {
      const dataJson = JSON.stringify(value, null, 2);
      await navigator.clipboard.writeText(dataJson);
      console.log(`${key} data copied to clipboard`);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = JSON.stringify(value, null, 2);
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  };

  const collapseAll = () => {
    setExpandedItems(new Set());
  };

  const copyRawObject = async () => {
    try {
      const rawJson = JSON.stringify(streamingState, null, 2);
      await navigator.clipboard.writeText(rawJson);
      // Could add a toast notification here if you have one
      console.log('Raw streaming state copied to clipboard');
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = JSON.stringify(streamingState, null, 2);
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  };

  // Object property renderer with expand functionality
  const renderObjectProperty = (key, value, parentPath = '') => {

    const formatSimpleValue = (val) => {
      if (val === null || val === undefined) {
        return <span className="value-null">null</span>;
      }
      if (typeof val === 'boolean') {
        return <StatusBadge status={val ? 'success' : 'error'} size="sm">{String(val)}</StatusBadge>;
      }
      if (val instanceof Date) {
        return <code>{val.toLocaleString()}</code>;
      }
      if (typeof val === 'string') {
        if (val.length > 100) {
          return (
            <details>
              <summary>({val.length} characters)</summary>
              <pre className="value-string-long-content">
                {val}
              </pre>
            </details>
          );
        }
        return <code>"{val}"</code>;
      }
      if (typeof val === 'number') {
        return <strong>{val}</strong>;
      }
      return String(val);
    };

    if (typeof value === 'object' && value !== null) {
      const objectKeys = Object.keys(value);
      const currentPath = parentPath ? `${parentPath}.${key}` : key;
      const isExpanded = expandedItems.has(currentPath);
      
      return (
        <div key={key} className="object-property">
          <div className="object-header">
            <strong>{key}:</strong>
            <span className="property-count">({objectKeys.length} properties)</span>
            <Button 
              size="sm" 
              variant="ghost" 
              onClick={() => toggleExpanded(currentPath)}
            >
              {isExpanded ? '▼' : '▶'} {isExpanded ? 'Collapse' : 'Expand'}
            </Button>
          </div>
          
          {isExpanded && (
            <div className="nested-object-container">
              {objectKeys.map(objKey => (
                <div key={objKey} className="nested-property">
                  <div className="nested-property-row">
                    <span className="property-key">{objKey}:</span>
                    <div>
                      {typeof value[objKey] === 'object' && value[objKey] !== null ? 
                        renderObjectProperty(objKey, value[objKey], currentPath) :
                        formatSimpleValue(value[objKey])
                      }
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }
    
    return formatSimpleValue(value);
  };

  // Simple value formatter for formatted view
  const formatValue = (key, value) => {
    if (typeof value === 'object' && value !== null) {
      return renderObjectProperty('root', value, key);
    }
    
    if (value === null || value === undefined) {
      return <span className="value-null">null</span>;
    }
    
    if (typeof value === 'boolean') {
      return <StatusBadge status={value ? 'success' : 'error'} size="sm">{String(value)}</StatusBadge>;
    }
    
    if (value instanceof Date) {
      return <code>{value.toLocaleString()}</code>;
    }
    
    if (typeof value === 'string') {
      if (value.length > 100) {
        return (
          <details>
            <summary>({value.length} characters)</summary>
            <pre className="value-string-long-content">
              {value}
            </pre>
          </details>
        );
      }
      return <code>"{value}"</code>;
    }
    
    if (typeof value === 'number') {
      return <strong>{value}</strong>;
    }
    
    return String(value);
  };

  return (
    <div>
      
      {/* Connection Controls */}
      <Card className="section-spacing">
        <CardSection>
          <div className="connection-controls">
            <StatusBadge status={streamingState.isConnected ? 'success' : 'error'} />
            <span>{streamingState.isConnected ? 'Connected' : 'Disconnected'}</span>
            <Button onClick={connect} disabled={streamingState.isConnected} size="sm">
              Connect
            </Button>
            <Button onClick={disconnect} disabled={!streamingState.isConnected} size="sm">
              Disconnect
            </Button>
          </div>
        </CardSection>
      </Card>

      {/* Connection Error */}
      {streamingState.connectionError && (
        <Alert type="error" className="section-spacing">
          {streamingState.connectionError}
        </Alert>
      )}

      {/* Control Buttons */}
      <Card className="section-spacing">
        <CardSection title="Controls">
          <div className="control-buttons">
            <Button onClick={expandAll} size="sm" variant="secondary">
              📂 Expand All
            </Button>
            <Button onClick={collapseAll} size="sm" variant="secondary">
              📁 Collapse All
            </Button>
            <Button 
              onClick={() => setShowRawMode(!showRawMode)} 
              size="sm" 
              variant={showRawMode ? 'primary' : 'secondary'}
            >
              {showRawMode ? '📋 Formatted View' : '🔍 Raw JSON View'}
            </Button>
            <Button onClick={copyRawObject} size="sm" variant="accent">
              📋 Copy All Data
            </Button>
          </div>
        </CardSection>
      </Card>

      {/* All State Keys */}
      <h2>All Streaming State ({allKeys.length} fields)</h2>
      
      {allKeys.map(key => (
        <Card key={key} className="card-spacing">
          {showRawMode ? (
            <CardSection 
              title={
                <div className="object-header">
                  <span>{key}</span>
                  <Button 
                    onClick={() => copyIndividualData(key, streamingState[key])} 
                    size="sm" 
                    variant="ghost"
                  >
                    📋 Copy
                  </Button>
                </div>
              }
            >
              <pre className="raw-json-pre">
                {JSON.stringify(streamingState[key], null, 2)}
              </pre>
            </CardSection>
          ) : (
            <CardSection title={key}>
              {formatValue(key, streamingState[key])}
            </CardSection>
          )}
        </Card>
      ))}

    </div>
  );
}

export default StreamingContextDiagnostic;