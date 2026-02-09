// Model pricing (USD per 1M tokens)
// 只有 API key 才會產生費用，OAuth/Token 訂閱制不計費
const PRICING = {
  'claude-sonnet-4-5': {
    input: 3.00 / 1000000,
    output: 15.00 / 1000000
  },
  'claude-opus-4-5': {
    input: 15.00 / 1000000,
    output: 75.00 / 1000000
  },
  'claude-haiku-4-5': {
    input: 0.80 / 1000000,
    output: 4.00 / 1000000
  },
  'gemini-2.5-pro': {
    input: 1.25 / 1000000,
    output: 5.00 / 1000000
  },
  'gemini-2.5-flash': {
    input: 0.075 / 1000000,
    output: 0.30 / 1000000
  },
  'gemini-2.0-flash': {
    input: 0.05 / 1000000,
    output: 0.20 / 1000000
  },
  'gemini-3-pro-preview': {
    input: 1.25 / 1000000,
    output: 5.00 / 1000000
  },
  'gemini-3-flash-preview': {
    input: 0.075 / 1000000,
    output: 0.30 / 1000000
  },
  'gpt-4o': {
    input: 2.50 / 1000000,
    output: 10.00 / 1000000
  },
  'gpt-4o-mini': {
    input: 0.15 / 1000000,
    output: 0.60 / 1000000
  },
  'gpt-5.1': {
    input: 2.00 / 1000000,
    output: 8.00 / 1000000
  },
  'gpt-5.2': {
    input: 2.50 / 1000000,
    output: 10.00 / 1000000
  },
  'gpt-5.3-codex': {
    input: 3.00 / 1000000,
    output: 12.00 / 1000000
  }
};

// 免費/訂閱制的 provider（不計費）
// - oauth: 訂閱制帳戶 (Claude Max, ChatGPT Plus, Google AI Studio 訂閱)
// - token: Anthropic Console OAuth token (Max 方案)
// - google 免費額度內也不計費
const FREE_PROVIDERS = [
  'anthropic',           // Max 方案 (token 類型)
  'google-antigravity',  // OAuth 訂閱
  'openai-codex',        // OAuth 訂閱 (ChatGPT Plus/Pro)
  'google-gemini-cli'    // OAuth (免費/訂閱)
];

// 只有這些 provider 使用 API key 會計費
const PAID_PROVIDERS = [
  'google',   // Google AI API key（超出免費額度才收費）
  'openai'    // OpenAI API key（按用量收費）
];

/**
 * 計算成本
 * @param {string} model - 模型名稱
 * @param {number} inputTokens - 輸入 token 數
 * @param {number} outputTokens - 輸出 token 數
 * @param {string} provider - Provider 名稱（可選，用於判斷是否免費）
 * @returns {number} 成本（USD）
 */
function calculateCost(model, inputTokens, outputTokens, provider = null) {
  // 如果指定了 provider 且在免費列表中，成本為 0
  if (provider && FREE_PROVIDERS.some(p => provider.startsWith(p))) {
    return 0;
  }
  
  // 從 model 名稱推斷 provider
  if (!provider) {
    if (model.includes('claude')) {
      // Anthropic 用的是 token (Max 方案)，不計費
      return 0;
    }
    if (model.includes('gpt')) {
      // OpenAI Codex 是 OAuth，不計費
      return 0;
    }
  }
  
  // 只有 google API key 才計費
  const price = PRICING[model];
  if (!price) {
    // 嘗試模糊匹配
    const modelKey = Object.keys(PRICING).find(k => model.includes(k));
    if (modelKey) {
      const p = PRICING[modelKey];
      return parseFloat(((inputTokens * p.input) + (outputTokens * p.output)).toFixed(6));
    }
    return 0;
  }
  
  const cost = (inputTokens * price.input) + (outputTokens * price.output);
  return parseFloat(cost.toFixed(6));
}

/**
 * 判斷是否為付費 provider
 */
function isPaidProvider(provider) {
  return PAID_PROVIDERS.some(p => provider === p || provider.startsWith(p + ':'));
}

/**
 * 判斷是否為免費/訂閱 provider
 */
function isFreeProvider(provider) {
  return FREE_PROVIDERS.some(p => provider === p || provider.startsWith(p));
}

module.exports = { PRICING, calculateCost, isPaidProvider, isFreeProvider, FREE_PROVIDERS, PAID_PROVIDERS };
