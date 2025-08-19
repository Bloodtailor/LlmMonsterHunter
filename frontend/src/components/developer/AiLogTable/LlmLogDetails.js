// LlmLogDetails - Displays detailed LLM log information in expanded row
// Shows model info, parameters, parsing results, and response text
// Used by AiLogTable when expanding LLM generation logs

import React from 'react';
import { StatusBadge, Card, CardSection } from '../../../shared/ui/index.js';

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
    <Card size='sm' variant='flat' background='dark'>
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '16px'
      }}>
        {/* Model Info */}
        <CardSection size='sm' title='Model Info'>
            <div><strong>Model:</strong> {llmLog.modelName || 'Unknown'}</div>
            <div><strong>Tokens:</strong> {llmLog.responseTokens || 0}</div>
            <div><strong>Speed:</strong> {llmLog.tokensPerSecond || 0} t/s</div>
        </CardSection>

        {/* Parameters */}
        <CardSection size='sm' title='Parameters'>
            <div><strong>max Tokens:</strong> {llmLog.maxTokens}</div>
            <div><strong>temperature:</strong> {llmLog.temperature}</div>
            <div><strong>top P:</strong> {llmLog.topP}</div>
            <div><strong>top K:</strong> {llmLog.topK}</div>
            <div><strong>repeat Penalty:</strong> {llmLog.repeatPenalty}</div>
            <div><strong>presence Penalty:</strong> {llmLog.presencePenalty}</div>
        </CardSection>

        {/* Parameters */}
        <CardSection size='sm' title='Parameters Cont.'>
            <div><strong>tfs Z:</strong> {llmLog.tfsZ}</div>
            <div><strong>typical P:</strong> {llmLog.typicalP}</div>
            <div><strong>mirostat Mode:</strong> {llmLog.mirostatMode}</div>
            <div><strong>mirostat Tau:</strong> {llmLog.mirostatTau}</div>
            <div><strong>mirostat Eta:</strong> {llmLog.mirostatEta}</div>
            <div><strong>seed:</strong> {llmLog.seed}</div>
            <div><strong>stop Sequences:</strong> {llmLog.stopSequences}</div>
        </CardSection>

        {/* Parsing */}
        <CardSection size='sm' title='Parsing'>
            <div>
              <strong>Success: </strong> {llmLog.parseSuccess ? 'Yes' : 'No'}
            </div>
        </CardSection>
      </div>
      
      {/* Response Text */}
      {llmLog.responseText && (
        <CardSection title='Response'>
          <Card >
            <div style={{
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              fontFamily: 'monospace'
            }}>
              {llmLog.responseText}
            </div>
          </Card>
        </CardSection>
      )}

      {/* Parsed Data */}
      {llmLog.parsedData && (
        <CardSection title="Parsed Data">
          <Card>
            <div style={{
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              fontFamily: 'monospace'
            }}>
              {JSON.stringify(llmLog.parsedData, null, 2)}
            </div>
          </Card>
        </CardSection>
      )}

      {/* Parser Config */}
      {llmLog.parserConfig && (
        <CardSection title="Parser Config">
          <Card>
            <div style={{
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              fontFamily: 'monospace'
            }}>
              {JSON.stringify(llmLog.parserConfig, null, 2)}
            </div>
          </Card>
        </CardSection>
      )}

      {/* Parser Error */}
      {llmLog.parseError && (
        <CardSection title="Parser Error">
          <Card>
            <div style={{
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              fontFamily: 'monospace'
            }}>
              {JSON.stringify(llmLog.parseError, null, 2)}
            </div>
          </Card>
        </CardSection>
      )}
    </Card>
  );
}

export default LlmLogDetails;
