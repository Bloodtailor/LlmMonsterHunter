// GenerationLogsScreen - Developer screen for viewing generation logs
// Simple wrapper around LlmLogTable component for easy testing and debugging
// Shows the expandable table functionality in action

import React from 'react';
import AiLogTableContainer from '../../components/developer/AiLogTable/AiLogTableContainer.js';
import { Card, CardSection } from '../../shared/ui/index.js';

/**
 * Developer screen for viewing generation logs with expandable details
 * Perfect for debugging generation system and testing table functionality
 * 
 * @returns {React.ReactElement} GenerationLogsScreen component
 */
function GenerationLogsScreen() {
  return (
    <div style={{ 
      padding: '20px',
      maxWidth: '100%',
      margin: '0 auto'
    }}>
      {/* Header */}
      <Card style={{ marginBottom: '20px' }}>
        <CardSection type="header" title="Generation Logs">
          <p style={{ 
            color: 'var(--text-dim)', 
            fontSize: 'var(--font-size-sm)',
            margin: '8px 0 0 0'
          }}>
            Monitor LLM and Image generation logs with expandable details. 
            Click any row to view detailed parameters, responses, and parsing results.
          </p>
        </CardSection>
      </Card>

      {/* Main Log Table */}
      <AiLogTableContainer />
      
      {/* Footer Info */}
      <Card style={{ marginTop: '20px' }}>
        <CardSection type="content">
          <div style={{ 
            fontSize: 'var(--font-size-sm)', 
            color: 'var(--text-dim)',
            textAlign: 'center'
          }}>
            <strong>Usage:</strong> Click rows to expand • Filter by type/status • 
            Refresh for latest logs • Supports up to 100 logs per page
          </div>
        </CardSection>
      </Card>
    </div>
  );
}

export default GenerationLogsScreen;