// ImageSettingsSection - the Images section of the settings panel
// Card art is painted by the Gemini image API ("Nano Banana"); this
// section owns the switch, the key, and the model pick: paste key →
// fetch the LIVE image-model list (success proves the key) → pick or
// type a model (empty keeps the game's default) → save → optional test
// paint through the real gateway, shown right here. Art is a BONUS -
// the game plays fully art-less while this is off.

import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Button, Input, LoadingSpinner, Select } from '../../shared/ui/index.js';
import { API_CONFIG, API_ENDPOINTS } from '../../api/core/config.js';
import * as settingsApi from '../../api/services/settings.js';

function ImageSettingsSection() {
  // The saved truth (masked), loaded on open
  const [settings, setSettings] = useState(null);
  const [loadError, setLoadError] = useState(null);

  // The form
  const [enabled, setEnabled] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState(''); // blank = keep stored key
  const [model, setModel] = useState('');
  const [typeModelManually, setTypeModelManually] = useState(false);

  // Fetch / save / test call states
  const [fetchedModels, setFetchedModels] = useState([]);
  const [fetchState, setFetchState] = useState({ busy: false, error: null });
  const [saveState, setSaveState] = useState({ busy: false, error: null, message: null });
  const [testState, setTestState] = useState({ busy: false, error: null, result: null });

  const loadSettings = useCallback(async () => {
    try {
      const loaded = await settingsApi.getImageSettings();
      setSettings(loaded);
      setEnabled(loaded.enabled);
      setModel(loaded.model || '');
      setLoadError(null);
    } catch (error) {
      setLoadError(error.message);
    }
  }, []);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const handleFetchModels = async () => {
    setFetchState({ busy: true, error: null });
    try {
      const result = await settingsApi.fetchGeminiModels(apiKeyInput.trim() || undefined);
      setFetchedModels(result.models);
      setFetchState({ busy: false, error: null });
    } catch (error) {
      setFetchedModels([]);
      setFetchState({ busy: false, error: error.message });
    }
  };

  const handleSave = async () => {
    setSaveState({ busy: true, error: null, message: null });
    setTestState({ busy: false, error: null, result: null });
    try {
      const saved = await settingsApi.saveImageSettings({
        enabled,
        apiKey: apiKeyInput.trim(),
        model: model.trim(),
      });
      setSettings(saved);
      setApiKeyInput(''); // the key is stored now - the panel never holds it
      setSaveState({ busy: false, error: null, message: saved.message || 'Settings saved' });
    } catch (error) {
      setSaveState({ busy: false, error: error.message, message: null });
    }
  };

  const handleTestPaint = async () => {
    setTestState({ busy: true, error: null, result: null });
    try {
      const result = await settingsApi.testImageGeneration();
      setTestState({ busy: false, error: null, result });
    } catch (error) {
      setTestState({ busy: false, error: error.message, result: null });
    }
  };

  if (loadError) {
    return (
      <Alert type="error" title="Settings unavailable">
        {loadError}
      </Alert>
    );
  }

  if (!settings) {
    return <LoadingSpinner />;
  }

  const keyOnFile = settings.hasApiKey;
  const canSave = !enabled || Boolean(keyOnFile || apiKeyInput.trim());
  const modelOptions = fetchedModels.length
    ? fetchedModels
    : [model || settings.defaultModel].filter(Boolean);
  const testImageUrl = testState.result?.imagePath
    ? `${API_CONFIG.BASE_URL}${API_ENDPOINTS.MONSTER_CARD_ART_FILE(testState.result.imagePath)}`
    : null;

  return (
    <div className="llm-settings">
      {/* The switch: painting on or off (art is a bonus either way) */}
      <div className="settings-provider-switch">
        <Button variant={enabled ? 'primary' : 'secondary'} onClick={() => setEnabled(true)}>
          🎨 Painting on
        </Button>
        <Button variant={!enabled ? 'primary' : 'secondary'} onClick={() => setEnabled(false)}>
          🚫 Off
        </Button>
      </div>

      <div className="settings-card">
        <div className="settings-field">
          <span className="settings-row-label">Gemini API key</span>
          <Input
            type="password"
            value={apiKeyInput}
            onChange={(event) => setApiKeyInput(event.target.value)}
            placeholder={
              keyOnFile ? `•••• ${settings.apiKeyLast4} (stored — paste to replace)` : 'AIza...'
            }
          />
          <p className="settings-hint">
            One key paints everything — monster card art, enemy faces, evolution repaints, and
            player portraits. Get one at aistudio.google.com.
          </p>
        </div>

        <div className="settings-field">
          <span className="settings-row-label">Model</span>
          <div className="settings-model-picker">
            {typeModelManually ? (
              <Input
                value={model}
                onChange={(event) => setModel(event.target.value)}
                placeholder={settings.defaultModel}
              />
            ) : (
              <Select
                options={modelOptions}
                value={model}
                onChange={(event) => setModel(event.target.value)}
                placeholder={`default: ${settings.defaultModel}`}
              />
            )}
            <Button size="sm" onClick={handleFetchModels} disabled={fetchState.busy}>
              {fetchState.busy ? 'Fetching…' : '🔄 Fetch models'}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setTypeModelManually(!typeModelManually)}
            >
              {typeModelManually ? 'Pick from list' : 'Type manually'}
            </Button>
          </div>
          <p className="settings-hint">
            Fetch pulls the live image-model list from Gemini with your key — a successful fetch
            means the key works. Leaving the pick empty keeps the game&apos;s default (
            {settings.defaultModel}, &quot;Nano Banana 2&quot;).
          </p>
          {fetchState.error && (
            <Alert type="error" title="Model fetch failed">
              {fetchState.error}
            </Alert>
          )}
        </div>
      </div>

      {/* Save + test paint */}
      <div className="settings-actions">
        <Button variant="primary" onClick={handleSave} disabled={!canSave || saveState.busy}>
          {saveState.busy ? 'Saving…' : '💾 Save'}
        </Button>
        <Button onClick={handleTestPaint} disabled={testState.busy || saveState.busy}>
          {testState.busy ? 'Painting…' : '🧪 Test paint'}
        </Button>
      </div>

      {!canSave && (
        <p className="settings-hint">Turning painting on needs a Gemini API key first.</p>
      )}

      {saveState.message && <Alert type="success">{saveState.message}</Alert>}
      {saveState.error && (
        <Alert type="error" title="Save failed">
          {saveState.error}
        </Alert>
      )}

      {testState.busy && (
        <p className="settings-hint">One small test image is on its way (a few seconds)…</p>
      )}
      {testState.result && (
        <div className="settings-card">
          <Alert type="success" title={`${testState.result.modelName || 'The model'} painted this`}>
            The image pipeline works end to end — card art will look like this style.
          </Alert>
          {testImageUrl && (
            <img className="settings-test-image" src={testImageUrl} alt="Test paint result" />
          )}
        </div>
      )}
      {testState.error && (
        <Alert type="error" title="Test paint failed">
          {testState.error}
        </Alert>
      )}
    </div>
  );
}

export default ImageSettingsSection;
