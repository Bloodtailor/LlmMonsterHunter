// Settings Transformers - snake_case settings API responses → camelCase
// Shapes the GET/PUT /api/settings/llm and /api/settings/image
// envelopes and the provider/paint test results for the settings panel

/**
 * Transform the LLM settings envelope (GET and PUT share the shape)
 * @param {object} rawSettings - Raw response from /api/settings/llm
 * @returns {object|null} Clean settings object or null if invalid
 */
export function transformLlmSettings(rawSettings) {
  if (!rawSettings || typeof rawSettings !== 'object') {
    console.warn('Invalid settings object provided to transformer');
    return null;
  }

  const local = rawSettings.local || {};
  const deepseek = rawSettings.deepseek || {};

  return {
    provider: rawSettings.provider ?? 'local',
    local: {
      configured: local.configured ?? false,
      modelFile: local.model_file ?? null,
      loaded: local.loaded ?? false,
      error: local.error ?? null,
      contextSize: local.context_size ?? 0,
      gpuLayers: local.gpu_layers ?? 0,
    },
    deepseek: {
      hasApiKey: deepseek.has_api_key ?? false,
      apiKeyLast4: deepseek.api_key_last4 ?? null,
      model: deepseek.model ?? null,
      contextWindow: deepseek.context_window ?? null,
    },
    knownModels: rawSettings.known_models ?? {},
    minContextWindow: rawSettings.min_context_window ?? 1000000,
    message: rawSettings.message ?? null,
  };
}

/**
 * Transform the provider-test result (POST /api/settings/llm/test)
 * @param {object} rawResult - Raw response
 * @returns {object|null} Clean test result or null if invalid
 */
export function transformProviderTest(rawResult) {
  if (!rawResult || typeof rawResult !== 'object') {
    console.warn('Invalid provider test object provided to transformer');
    return null;
  }

  return {
    text: rawResult.text ?? '',
    provider: rawResult.provider ?? null,
    modelName: rawResult.model_name ?? null,
    promptTokens: rawResult.prompt_tokens ?? null,
  };
}

/**
 * Transform the image settings envelope (GET and PUT share the shape)
 * @param {object} rawSettings - Raw response from /api/settings/image
 * @returns {object|null} Clean settings object or null if invalid
 */
export function transformImageSettings(rawSettings) {
  if (!rawSettings || typeof rawSettings !== 'object') {
    console.warn('Invalid image settings object provided to transformer');
    return null;
  }

  return {
    enabled: rawSettings.enabled ?? false,
    hasApiKey: rawSettings.has_api_key ?? false,
    apiKeyLast4: rawSettings.api_key_last4 ?? null,
    model: rawSettings.model ?? null,
    defaultModel: rawSettings.default_model ?? null,
    message: rawSettings.message ?? null,
  };
}

/**
 * Transform the test-paint result (POST /api/settings/image/test)
 * @param {object} rawResult - Raw response
 * @returns {object|null} Clean test result or null if invalid
 */
export function transformImageTest(rawResult) {
  if (!rawResult || typeof rawResult !== 'object') {
    console.warn('Invalid image test object provided to transformer');
    return null;
  }

  return {
    imagePath: rawResult.image_path ?? null,
    modelName: rawResult.model_name ?? null,
  };
}
