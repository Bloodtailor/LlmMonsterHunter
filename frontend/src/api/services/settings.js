// Settings Service - the settings panel's HTTP surface
// GET/PUT the LLM and image configurations, fetch the live model lists
// (which double as key validation), and fire test generations/paints.
// Validation failures come back as HTTP 400 whose real message lives in
// the body's `error` field - the shared client throws a generic ApiError
// for those, so every call here unwraps the backend's own words (the
// panel must show "Gemini rejected the API key (401)...", not
// "API request failed: 400").

import { get, post, put } from '../core/client.js';
import {
  transformImageSettings,
  transformImageTest,
  transformLlmSettings,
  transformProviderTest,
} from '../transformers/settings.js';

export async function getLlmSettings() {
  const response = await withBackendMessage(get('/api/settings/llm'));
  return transformLlmSettings(response);
}

/**
 * Save the panel's form. A blank apiKey means "keep the stored key".
 * @param {object} form - { provider, apiKey, model, contextWindow }
 */
export async function saveLlmSettings(form) {
  const response = await withBackendMessage(
    put('/api/settings/llm', {
      provider: form.provider,
      deepseek: {
        api_key: form.apiKey || '',
        model: form.model || '',
        context_window: form.contextWindow ?? '',
      },
    }),
  );
  return transformLlmSettings(response);
}

/**
 * Live model list from DeepSeek, proxied by the backend. Success proves
 * the key works. Omit apiKey to use the stored one.
 */
export async function fetchDeepseekModels(apiKey) {
  const response = await withBackendMessage(
    post('/api/settings/llm/fetch-models', apiKey ? { api_key: apiKey } : {}),
  );
  return {
    models: response.models ?? [],
    knownModels: response.known_models ?? {},
  };
}

/**
 * One tiny real generation through the normal gateway - it streams in
 * the streaming panel (titled with the model) and lands in the dev log.
 */
export async function testLlmGeneration() {
  const response = await withBackendMessage(post('/api/settings/llm/test'));
  return transformProviderTest(response);
}

export async function getImageSettings() {
  const response = await withBackendMessage(get('/api/settings/image'));
  return transformImageSettings(response);
}

/**
 * Save the Images section. A blank apiKey means "keep the stored key".
 * @param {object} form - { enabled, apiKey, model }
 */
export async function saveImageSettings(form) {
  const response = await withBackendMessage(
    put('/api/settings/image', {
      enabled: Boolean(form.enabled),
      api_key: form.apiKey || '',
      model: form.model || '',
    }),
  );
  return transformImageSettings(response);
}

/**
 * Live image-capable model list from Gemini, proxied by the backend.
 * Success proves the key works. Omit apiKey to use the stored one.
 */
export async function fetchGeminiModels(apiKey) {
  const response = await withBackendMessage(
    post('/api/settings/image/fetch-models', apiKey ? { api_key: apiKey } : {}),
  );
  return { models: response.models ?? [] };
}

/**
 * One tiny real paint through the normal gateway - it queues, lands in
 * the dev log with its model, and files an image the panel shows.
 */
export async function testImageGeneration() {
  const response = await withBackendMessage(post('/api/settings/image/test'));
  return transformImageTest(response);
}

/** Unwrap the backend's `error` field from a 4xx body, if there is one */
async function withBackendMessage(requestPromise) {
  try {
    return await requestPromise;
  } catch (error) {
    const body = error?.response?.json ? await error.response.json().catch(() => null) : null;
    if (body?.error) {
      throw new Error(body.error);
    }
    throw error;
  }
}
