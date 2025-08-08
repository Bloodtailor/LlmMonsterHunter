// LlmLogDetails - Displays detailed LLM log information in expanded row
// Shows model info, parameters, parsing results, and response text
// Used by AiLogTable when expanding LLM generation logs

import React from 'react';
import { StatusBadge } from '../../../shared/ui/index.js';

/**
 * LlmLogDetails - Displays detailed LLM log information
 * @param {object} props - Component props
 * @param {object} props.log - Generation log object
 * @returns {React.ReactElement} LlmLogDetails component
 */
function LlmLogDetails({ log }) {
  const llmLog = log.llmLogId;
  
  if (!llmLog) {
    return (
      <div style={{ padding: '16px', color: 'var(--text-dim)' }}>
        No LLM log details available.
      </div>
    );
  }

  return (
    <div style={{ padding: '16px', background: 'var(--background-dark)' }}>
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '16px',
        marginBottom: '16px'
      }}>
        {/* Model Info */}
        <div>
          <h4 style={{ margin: '0 0 8px 0', color: 'var(--text-light)' }}>Model Info</h4>
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-dim)' }}>
            <div><strong>Model:</strong> {llmLog.modelName || 'Unknown'}</div>
            <div><strong>Tokens:</strong> {llmLog.responseTokens || 0}</div>
            <div><strong>Speed:</strong> {llmLog.tokensPerSecond || 0} t/s</div>
          </div>
        </div>

        {/* Parameters */}
        <div>
          <h4 style={{ margin: '0 0 8px 0', color: 'var(--text-light)' }}>Parameters</h4>
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-dim)' }}>
            <div><strong>Temperature:</strong> {llmLog.temperature || 0}</div>
            <div><strong>Max Tokens:</strong> {llmLog.maxTokens || 0}</div>
            <div><strong>Top P:</strong> {llmLog.topP || 0}</div>
            <div><strong>Seed:</strong> {llmLog.seed || 'None'}</div>
          </div>
        </div>

        {/* Parsing */}
        <div>
          <h4 style={{ margin: '0 0 8px 0', color: 'var(--text-light)' }}>Parsing</h4>
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-dim)' }}>
            <div>
              <strong>Success:</strong> 
              <StatusBadge type={llmLog.parseSuccess ? 'success' : 'error'} style={{ marginLeft: '8px' }}>
                {llmLog.parseSuccess ? 'Yes' : 'No'}
              </StatusBadge>
            </div>
            {llmLog.parseError && (
              <div style={{ marginTop: '4px', color: 'var(--color-red-intense)' }}>
                <strong>Error:</strong> {llmLog.parseError}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Response Text */}
      {llmLog.responseText && (
        <div>
          <h4 style={{ margin: '0 0 8px 0', color: 'var(--text-light)' }}>Response</h4>
          <div style={{
            background: 'var(--background-medium)',
            padding: '12px',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--text-light)',
            maxHeight: '200px',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace'
          }}>
            {llmLog.responseText.length > 500 
              ? `${llmLog.responseText.slice(0, 500)}...` 
              : llmLog.responseText
            }
          </div>
        </div>
      )}
    </div>
  );
}

export default LlmLogDetails;