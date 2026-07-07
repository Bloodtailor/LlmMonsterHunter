// LlmSettingsSection - the Text Generation section of the settings panel
// Provider switch (Local model / DeepSeek API), the local model's
// read-only status, and the DeepSeek setup flow: paste key → fetch the
// LIVE model list (success proves the key) → pick or type a model →
// context window auto-fills from the known-models map (always editable)
// → save → optional test generation through the real gateway.

import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Button,
  Input,
  LoadingSpinner,
  Select,
  StatusBadge,
} from '../../shared/ui/index.js';
import * as settingsApi from '../../api/services/settings.js';

const PROVIDER_OPTIONS = [
  { id: 'local', label: '💻 Local model' },
  { id: 'deepseek', label: '☁️ DeepSeek API' },
];

function LlmSettingsSection() {
  // The saved truth (masked), loaded on open
  const [settings, setSettings] = useState(null);
  const [loadError, setLoadError] = useState(null);

  // The form
  const [provider, setProvider] = useState('local');
  const [apiKeyInput, setApiKeyInput] = useState(''); // blank = keep stored key
  const [model, setModel] = useState('');
  const [contextWindow, setContextWindow] = useState('');
  const [typeModelManually, setTypeModelManually] = useState(false);

  // Fetch / save / test call states
  const [fetchedModels, setFetchedModels] = useState([]);
  const [fetchState, setFetchState] = useState({ busy: false, error: null });
  const [saveState, setSaveState] = useState({ busy: false, error: null, message: null });
  const [testState, setTestState] = useState({ busy: false, error: null, result: null });

  const loadSettings = useCallback(async () => {
    try {
      const loaded = await settingsApi.getLlmSettings();
      setSettings(loaded);
      setProvider(loaded.provider);
      setModel(loaded.deepseek.model || '');
      setContextWindow(loaded.deepseek.contextWindow ? String(loaded.deepseek.contextWindow) : '');
      setLoadError(null);
    } catch (error) {
      setLoadError(error.message);
    }
  }, []);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const knownModels = settings?.knownModels || {};

  const handleModelChange = (nextModel) => {
    setModel(nextModel);
    // Known models auto-fill their window; the field stays editable
    if (knownModels[nextModel]) {
      setContextWindow(String(knownModels[nextModel]));
    }
  };

  const handleFetchModels = async () => {
    setFetchState({ busy: true, error: null });
    try {
      const result = await settingsApi.fetchDeepseekModels(apiKeyInput.trim() || undefined);
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
      const saved = await settingsApi.saveLlmSettings({
        provider,
        apiKey: apiKeyInput.trim(),
        model: model.trim(),
        contextWindow: contextWindow === '' ? '' : Number(contextWindow),
      });
      setSettings(saved);
      setApiKeyInput(''); // the key is stored now - the panel never holds it
      setSaveState({ busy: false, error: null, message: saved.message || 'Settings saved' });
    } catch (error) {
      setSaveState({ busy: false, error: error.message, message: null });
    }
  };

  const handleTestGeneration = async () => {
    setTestState({ busy: true, error: null, result: null });
    try {
      const result = await settingsApi.testLlmGeneration();
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

  const keyOnFile = settings.deepseek.hasApiKey;
  const canSaveDeepseek = Boolean(
    (keyOnFile || apiKeyInput.trim()) && model.trim() && contextWindow,
  );
  const canSave = provider === 'local' || canSaveDeepseek;
  const modelIsKnown = Boolean(knownModels[model]);

  return (
    <div className="llm-settings">
      {/* Provider switch */}
      <div className="settings-provider-switch">
        {PROVIDER_OPTIONS.map((option) => (
          <Button
            key={option.id}
            variant={provider === option.id ? 'primary' : 'secondary'}
            onClick={() => setProvider(option.id)}
          >
            {option.label}
          </Button>
        ))}
      </div>

      {/* Local model - read-only in v1, .env owns it */}
      {provider === 'local' && (
        <div className="settings-card">
          <div className="settings-row">
            <span className="settings-row-label">Model file</span>
            <span>{settings.local.modelFile || 'not configured'}</span>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Status</span>
            <StatusBadge status={settings.local.loaded ? 'success' : 'warning'}>
              {settings.local.loaded ? 'loaded' : 'not loaded (loads on first use)'}
            </StatusBadge>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Context window</span>
            <span>{settings.local.contextSize.toLocaleString()} tokens</span>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">GPU layers</span>
            <span>{settings.local.gpuLayers}</span>
          </div>
          {settings.local.error && (
            <Alert type="warning" title="Last load error">
              {settings.local.error}
            </Alert>
          )}
          <p className="settings-hint">
            The local model is configured in <code>.env</code> (path, context size, GPU layers) —
            restart the backend after changing it. Switching providers here needs no restart.
          </p>
        </div>
      )}

      {/* DeepSeek setup */}
      {provider === 'deepseek' && (
        <div className="settings-card">
          <div className="settings-field">
            <span className="settings-row-label">API key</span>
            <Input
              type="password"
              value={apiKeyInput}
              onChange={(event) => setApiKeyInput(event.target.value)}
              placeholder={
                keyOnFile
                  ? `•••• ${settings.deepseek.apiKeyLast4} (stored — paste to replace)`
                  : 'sk-...'
              }
            />
          </div>

          <div className="settings-field">
            <span className="settings-row-label">Model</span>
            <div className="settings-model-picker">
              {typeModelManually ? (
                <Input
                  value={model}
                  onChange={(event) => handleModelChange(event.target.value)}
                  placeholder="deepseek-v4-flash"
                />
              ) : (
                <Select
                  options={fetchedModels.length ? fetchedModels : Object.keys(knownModels)}
                  value={model}
                  onChange={(event) => handleModelChange(event.target.value)}
                  placeholder="pick a model"
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
              Fetch pulls the live list from DeepSeek with your key — a successful fetch means the
              key works. New DeepSeek models appear here the day they ship; typing manually covers
              the rest.
            </p>
            {fetchState.error && (
              <Alert type="error" title="Model fetch failed">
                {fetchState.error}
              </Alert>
            )}
          </div>

          <div className="settings-field">
            <span className="settings-row-label">Context window (tokens)</span>
            <Input
              type="number"
              value={contextWindow}
              onChange={(event) => setContextWindow(event.target.value)}
              placeholder={`at least ${settings.minContextWindow}`}
            />
            {!modelIsKnown && model && !contextWindow && (
              <Alert type="warning" title="Unknown model">
                This game doesn't know “{model}” — set its context window manually (DeepSeek's API
                doesn't publish sizes).
              </Alert>
            )}
            <p className="settings-hint">
              Auto-fills for known models, always editable. Bigger windows mean prompts are never
              trimmed and every prompt token is billed — a working window like 65536 is plenty.
            </p>
          </div>
        </div>
      )}

      {/* Save + test */}
      <div className="settings-actions">
        <Button variant="primary" onClick={handleSave} disabled={!canSave || saveState.busy}>
          {saveState.busy ? 'Saving…' : '💾 Save'}
        </Button>
        <Button onClick={handleTestGeneration} disabled={testState.busy || saveState.busy}>
          {testState.busy ? 'Generating…' : '🧪 Test generation'}
        </Button>
      </div>

      {saveState.message && <Alert type="success">{saveState.message}</Alert>}
      {saveState.error && (
        <Alert type="error" title="Save failed">
          {saveState.error}
        </Alert>
      )}

      {testState.busy && (
        <p className="settings-hint">Watch the streaming panel — it names the model speaking.</p>
      )}
      {testState.result && (
        <Alert
          type="success"
          title={`${testState.result.modelName || 'The model'} answered (${
            testState.result.promptTokens ?? '?'
          } prompt tokens)`}
        >
          {testState.result.text}
        </Alert>
      )}
      {testState.error && (
        <Alert type="error" title="Test generation failed">
          {testState.error}
        </Alert>
      )}
    </div>
  );
}

export default LlmSettingsSection;
