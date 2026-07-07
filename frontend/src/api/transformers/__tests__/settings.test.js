import {
  transformImageSettings,
  transformImageTest,
  transformLlmSettings,
  transformProviderTest,
} from '../settings.js';

const RAW_SETTINGS = {
  success: true,
  provider: 'deepseek',
  local: {
    configured: true,
    model_file: 'qwen3-14b.gguf',
    loaded: false,
    error: null,
    context_size: 8192,
    gpu_layers: 35,
  },
  deepseek: {
    has_api_key: true,
    api_key_last4: '1234',
    model: 'deepseek-v4-flash',
    context_window: 2000000,
  },
  known_models: { 'deepseek-v4-flash': 1000000 },
  min_context_window: 1000000,
  message: 'Settings saved',
};

describe('transformLlmSettings', () => {
  it('maps snake_case fields to camelCase', () => {
    const settings = transformLlmSettings(RAW_SETTINGS);
    expect(settings.provider).toBe('deepseek');
    expect(settings.local.modelFile).toBe('qwen3-14b.gguf');
    expect(settings.local.contextSize).toBe(8192);
    expect(settings.deepseek.hasApiKey).toBe(true);
    expect(settings.deepseek.apiKeyLast4).toBe('1234');
    expect(settings.deepseek.contextWindow).toBe(2000000);
    expect(settings.knownModels['deepseek-v4-flash']).toBe(1000000);
    expect(settings.minContextWindow).toBe(1000000);
    expect(settings.message).toBe('Settings saved');
  });

  it('fills safe defaults for a bare local response', () => {
    const settings = transformLlmSettings({ success: true, provider: 'local' });
    expect(settings.provider).toBe('local');
    expect(settings.local.configured).toBe(false);
    expect(settings.deepseek.hasApiKey).toBe(false);
    expect(settings.knownModels).toEqual({});
    expect(settings.message).toBeNull();
  });

  it('returns null (with a warning) for invalid input', () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => {});
    expect(transformLlmSettings(null)).toBeNull();
    expect(transformLlmSettings('nope')).toBeNull();
    warn.mockRestore();
  });
});

describe('transformProviderTest', () => {
  it('maps the test result', () => {
    const result = transformProviderTest({
      success: true,
      text: 'The referee is ready.',
      provider: 'deepseek',
      model_name: 'deepseek-v4-flash',
      prompt_tokens: 31,
    });
    expect(result.text).toBe('The referee is ready.');
    expect(result.modelName).toBe('deepseek-v4-flash');
    expect(result.promptTokens).toBe(31);
  });

  it('keeps prompt tokens null when the provider never reported them', () => {
    const result = transformProviderTest({ success: true, text: 'hi', provider: 'local' });
    expect(result.promptTokens).toBeNull();
    expect(result.modelName).toBeNull();
  });

  it('returns null (with a warning) for invalid input', () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => {});
    expect(transformProviderTest(undefined)).toBeNull();
    warn.mockRestore();
  });
});

describe('transformImageSettings', () => {
  it('maps snake_case fields to camelCase', () => {
    const settings = transformImageSettings({
      success: true,
      enabled: true,
      has_api_key: true,
      api_key_last4: '5678',
      model: 'gemini-3.1-flash-image',
      default_model: 'gemini-3.1-flash-image',
      message: 'Settings saved',
    });
    expect(settings.enabled).toBe(true);
    expect(settings.hasApiKey).toBe(true);
    expect(settings.apiKeyLast4).toBe('5678');
    expect(settings.model).toBe('gemini-3.1-flash-image');
    expect(settings.defaultModel).toBe('gemini-3.1-flash-image');
    expect(settings.message).toBe('Settings saved');
  });

  it('fills safe defaults for a bare response', () => {
    const settings = transformImageSettings({ success: true });
    expect(settings.enabled).toBe(false);
    expect(settings.hasApiKey).toBe(false);
    expect(settings.model).toBeNull();
  });

  it('returns null (with a warning) for invalid input', () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => {});
    expect(transformImageSettings(null)).toBeNull();
    warn.mockRestore();
  });
});

describe('transformImageTest', () => {
  it('maps the test paint result', () => {
    const result = transformImageTest({
      success: true,
      image_path: 'settings/00000001.png',
      model_name: 'gemini-3.1-flash-image',
    });
    expect(result.imagePath).toBe('settings/00000001.png');
    expect(result.modelName).toBe('gemini-3.1-flash-image');
  });

  it('returns null (with a warning) for invalid input', () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => {});
    expect(transformImageTest('nope')).toBeNull();
    warn.mockRestore();
  });
});
