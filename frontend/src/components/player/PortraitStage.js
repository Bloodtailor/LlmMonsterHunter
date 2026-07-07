// PortraitStage.js - the character's face, on the player's terms
// Paint candidates from the (editable) appearance brief, as many as
// wanted; upload an image instead; click any candidate to make it THE
// portrait. Art never blocks: "Begin your story" works with or without
// a portrait, and a disabled image pipeline just hides the paint button.

import React, { useRef, useState } from 'react';
import { Alert, Button, Card, CardSection, Textarea } from '../../shared/ui/index.js';
import { useEventSubscription } from '../../api/events/useEventSubscription.js';
import * as playerApi from '../../api/services/player.js';

const candidateStyles = (isSelected) => ({
  width: '160px',
  height: '160px',
  objectFit: 'cover',
  borderRadius: 'var(--border-radius-md, 8px)',
  border: isSelected
    ? '3px solid var(--color-primary, #7b5cff)'
    : '1px solid var(--color-border, #444)',
  cursor: 'pointer',
});

function PortraitStage({ player, onDone }) {
  const appearance = player?.appearance?.visual_description || player?.description || '';
  const [brief, setBrief] = useState(appearance);
  const [candidates, setCandidates] = useState([]);
  const [selectedPath, setSelectedPath] = useState(player?.cardArt?.relativePath || null);
  const [isPainting, setIsPainting] = useState(false);
  const [paintUnavailable, setPaintUnavailable] = useState(false);
  const [error, setError] = useState(null);

  const paintWorkflowIdRef = useRef(null);
  const fileInputRef = useRef(null);

  const paint = async () => {
    setError(null);
    setIsPainting(true);
    try {
      const result = await playerApi.generatePortrait(brief);
      if (!result.success || !result.workflowId) {
        // A disabled image pipeline is a normal world state, not an error
        if ((result.error || '').includes('disabled')) {
          setPaintUnavailable(true);
        } else {
          setError(result.error || 'The paint would not take - try again.');
        }
        setIsPainting(false);
        return;
      }
      paintWorkflowIdRef.current = result.workflowId;
    } catch (paintError) {
      setError(paintError.message || 'The paint would not take - try again.');
      setIsPainting(false);
    }
  };

  useEventSubscription('workflowCompleted', ({ workflowId, result }) => {
    if (workflowId !== paintWorkflowIdRef.current) return;
    paintWorkflowIdRef.current = null;
    if (result?.image_path) {
      setCandidates((current) => [...current, result.image_path]);
    }
    setIsPainting(false);
  });

  useEventSubscription('workflowFailed', ({ workflowId, error: failure }) => {
    if (workflowId !== paintWorkflowIdRef.current) return;
    paintWorkflowIdRef.current = null;
    setError(
      (typeof failure === 'object' ? failure?.error : failure) ||
        'The paint would not take - try again.',
    );
    setIsPainting(false);
  });

  const choose = async (imagePath) => {
    setError(null);
    const result = await playerApi.selectPortrait(imagePath);
    if (result.success) {
      setSelectedPath(result.imagePath);
    } else {
      setError(result.error || 'That image refused the frame.');
    }
  };

  const handleUpload = async (event) => {
    const file = event.target.files && event.target.files[0];
    event.target.value = ''; // the same file can be re-picked later
    if (!file) return;
    setError(null);
    const result = await playerApi.uploadPortrait(file);
    if (result.success && result.imagePath) {
      setCandidates((current) => [...current, result.imagePath]);
      setSelectedPath(result.imagePath); // uploads auto-select on the backend
    } else {
      setError(result.error || 'The upload was refused.');
    }
  };

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="lg" title="🖼️ Your portrait" alignment="center">
        <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
          Paint from your appearance, upload your own image, or walk in faceless - the story starts
          either way.
        </p>
      </CardSection>

      <CardSection type="content" padding="lg">
        {error && (
          <Alert type="error" title="Portrait trouble">
            {String(error)}
          </Alert>
        )}

        <Textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          placeholder="The artist's brief - what should the portrait show?"
          rows={3}
        />

        <div
          style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'center',
            flexWrap: 'wrap',
            marginTop: '16px',
          }}
        >
          {!paintUnavailable && (
            <Button size="lg" variant="primary" icon="🎨" disabled={isPainting} onClick={paint}>
              {isPainting ? 'Painting...' : candidates.length ? 'Paint another' : 'Paint portrait'}
            </Button>
          )}
          <Button
            size="lg"
            variant="secondary"
            icon="📁"
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
          >
            Upload an image
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            style={{ display: 'none' }}
            onChange={handleUpload}
          />
        </div>

        {paintUnavailable && (
          <p
            style={{
              color: 'var(--color-text-secondary)',
              textAlign: 'center',
              marginTop: '12px',
            }}
          >
            The painter is away (image generation is disabled) - uploads still work.
          </p>
        )}

        {candidates.length > 0 && (
          <div
            style={{
              display: 'flex',
              gap: '12px',
              flexWrap: 'wrap',
              justifyContent: 'center',
              marginTop: '20px',
            }}
          >
            {candidates.map((path) => (
              <img
                key={path}
                src={playerApi.getPortraitUrl(path)}
                alt="Portrait candidate"
                style={candidateStyles(path === selectedPath)}
                onClick={() => choose(path)}
              />
            ))}
          </div>
        )}
        {candidates.length > 0 && (
          <p
            style={{
              color: 'var(--color-text-secondary)',
              textAlign: 'center',
              margin: '8px 0 0',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            Click a portrait to make it yours.
          </p>
        )}
      </CardSection>

      <CardSection type="content" alignment="center" padding="sm">
        <Button size="xl" variant="primary" icon="✨" disabled={isPainting} onClick={onDone}>
          {selectedPath ? 'Begin your story' : 'Begin your story (no portrait)'}
        </Button>
      </CardSection>
    </Card>
  );
}

export default PortraitStage;
