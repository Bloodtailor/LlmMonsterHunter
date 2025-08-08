/**
 * Transform raw log object into clean game object
 * @param {object} rawMonster - Raw log object from API
 * @returns {object|null} Clean log object or null if invalid
 */
export function transformGenerationLog(rawLog) {
  if (!rawLog || !rawLog.id) {
    console.warn('Invalid log object provided to transformer');
    return null;
  }

  return {
    id: rawLog.id,

    generationType: rawLog.generation_type ?? '',
    promptType: rawLog.prompt_type ?? '',
    promptName: rawLog.prompt_name ?? '',
    promptText: rawLog.prompt_text ?? '',
    
    status: rawLog.status ?? '',
    priority: rawLog.priority ?? 0,
    
    generationAttempt: rawLog.generation_attempt ?? 0,
    maxAttempts: rawLog.max_attempts ?? 0,

    startTime: rawLog.start_time ? new Date(rawLog.start_time) : null,
    endTime: rawLog.end_time ? new Date(rawLog.end_time) : null,
    
    durationSeconds: rawLog.duration_seconds ? Math.floor(rawLog.duration_seconds) : 0,

    errorMessage: rawLog.error_message ?? '',
    
    llmLogId: rawLog.llm_data ? transformLlmLog(rawLog.llm_data) : [],
    imageLogId: rawLog.image_data ? transformImageLog(rawLog.image_data): []
  };
}

/**
 * Transform array of raw logs into clean game objects
 * @param {Array} rawLogs - Array of raw log objects from API
 * @returns {Array} Array of clean log objects (filters out invalid ones)
 */
export function transformGenerationLogs(rawLogs) {

    if (!Array.isArray(rawLogs)) {
    console.warn('transformGenerationLogs expects an array, received:', typeof rawLogs);
    return [];
  }

  return rawLogs
    .map(transformGenerationLog)
    .filter(Boolean); // Remove any null results from invalid abilities

}

/**
 * Transform raw LLM log object into clean object with safe defaults
 * @param {object} rawLlmLog - Raw LLM log object from API
 * @returns {object|null} Clean LLM log object or null if invalid
 */
export function transformLlmLog(rawLlmLog) {
  if (!rawLlmLog || typeof rawLlmLog !== 'object') {
    console.warn('Invalid LLM log object provided to transformer');
    return null;
  }

  return {
    // === LLM Inference Parameters ===
    maxTokens: rawLlmLog.max_tokens ?? 0,
    temperature: rawLlmLog.temperature ?? 0,
    topP: rawLlmLog.top_p ?? 0,
    topK: rawLlmLog.top_k ?? 0,
    repeatPenalty: rawLlmLog.repeat_penalty ?? 0,
    frequencyPenalty: rawLlmLog.frequency_penalty ?? 0,
    presencePenalty: rawLlmLog.presence_penalty ?? 0,
    tfsZ: rawLlmLog.tfs_z ?? 0,
    typicalP: rawLlmLog.typical_p ?? 0,
    mirostatMode: rawLlmLog.mirostat_mode ?? 0,
    mirostatTau: rawLlmLog.mirostat_tau ?? 0,
    mirostatEta: rawLlmLog.mirostat_eta ?? 0,
    seed: rawLlmLog.seed ?? 0,
    stopSequences: rawLlmLog.stop_sequences ?? [],

    echo: rawLlmLog.echo ?? false,

    // === Model Info ===
    modelName: rawLlmLog.model_name ?? '',

    // === LLM Response ===
    responseText: rawLlmLog.response_text ?? '',
    responseTokens: rawLlmLog.response_tokens ?? 0,
    tokensPerSecond: rawLlmLog.tokens_per_second ?? 0,

    // === Parsing ===
    parserConfig: rawLlmLog.parser_config ?? {},
    parseSuccess: rawLlmLog.parse_success ?? false,
    parsedData: rawLlmLog.parsed_data ?? {},
    parseError: rawLlmLog.parse_error ?? '',
  };
}

/**
 * Transform raw Image log object into clean object with safe defaults
 * @param {object} rawImageLog - Raw image log object from API
 * @returns {object|null} Clean image log object or null if invalid
 */
export function transformImageLog(rawImageLog) {
  if (!rawImageLog || typeof rawImageLog !== 'object') {
    console.warn('Invalid image log object provided to transformer');
    return null;
  }

  return {
    imagePath: rawImageLog.image_path ?? '',
    imageFilename: rawImageLog.image_filename ?? '',
  };
}
