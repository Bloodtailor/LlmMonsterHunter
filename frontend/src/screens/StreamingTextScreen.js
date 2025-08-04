// StreamingTextScreen - Clean separation of concerns
// Uses StreamingContextDiagnostic component for state display
// Includes monster generation button to test streaming with real operations

import React from 'react';
import { Button, Alert, StatusBadge, Card, CardSection} from '../shared/ui/index.js';
import { useMonsterGeneration } from '../app/hooks/useMonsters.js';
import StreamingContextDiagnostic from '../components/streaming/StreamingContextDiagnostic.js';

function StreamingTextScreen() {
  
  // Monster generation hook for testing streaming
  const {
    generationResult,
    monster: generatedMonster,
    isGenerating,
    isError: isGenerationError,
    error: generationError,
    generate
  } = useMonsterGeneration();

  // Handle monster generation
  const handleGenerateMonster = async () => {
    console.log('🎲 Generating new monster...');
    await generate({
      prompt_name: 'detailed_monster',
      generate_card_art: true
    });
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Header */}
      <h1>🧪 Streaming Context Test</h1>
      <p>Test streaming context state display</p>

      {/* Monster Generation Section */}
      <div>
        <h2 style={{ marginBottom: '1rem', color: 'var(--color-text-primary, #333)' }}>
          🎲 Generate Monster (Test Streaming)
        </h2>
        <p style={{ marginBottom: '1.5rem', color: 'var(--color-text-secondary, #666)' }}>
          Generate a monster to see real LLM and Image streaming events in the diagnostic panel below
        </p>
        
        <Button
          variant="primary"
          size="lg"
          onClick={handleGenerateMonster}
          disabled={isGenerating}
          style={{
            fontSize: '16px',
            padding: '12px 24px',
            minWidth: '200px'
          }}
        >
          {isGenerating ? (
            <>
              <span style={{ marginRight: '8px' }}>🔄</span>
              Generating...
            </>
          ) : (
            <>
              <span style={{ marginRight: '8px' }}>✨</span>
              Generate Monster
            </>
          )}
        </Button>

        {/* Generation Status */}
        <div style={{ marginTop: '1.5rem' }}>
          {isGenerating && (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              gap: '10px',
              marginBottom: '1rem'
            }}>
              <StatusBadge status="warning" size="md" />
              <span>Creating your monster with AI... Watch the streaming events below!</span>
            </div>
          )}

          {generationResult?.success && generatedMonster && (
            <Alert type="success" size="md" style={{ maxWidth: '600px', margin: '0 auto' }}>
              <strong>🎉 Success!</strong> Generated "{generatedMonster.name}" - {generatedMonster.species}
            </Alert>
          )}

          {isGenerationError && (
            <Alert type="error" size="md" style={{ maxWidth: '600px', margin: '0 auto' }}>
              <strong>❌ Generation Failed:</strong> {generationError?.message || 'Unknown error occurred'}
            </Alert>
          )}
        </div>
      </div>

      {/* Streaming Context Diagnostic */}
      <div>
        <h2 style={{ marginBottom: '1rem', color: 'var(--color-text-primary, #333)' }}>
          📊 Streaming Context Diagnostic
        </h2>
        <p style={{ marginBottom: '2rem', color: 'var(--color-text-secondary, #666)' }}>
          Real-time display of all streaming context states. Generate a monster above to see events populate.
        </p>
        
        <StreamingContextDiagnostic />
      </div>

    </div>
  );
}

export default StreamingTextScreen;