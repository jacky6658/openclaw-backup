// Model pricing (USD per 1M tokens)
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
  'gpt-4o': {
    input: 2.50 / 1000000,
    output: 10.00 / 1000000
  },
  'gpt-4o-mini': {
    input: 0.15 / 1000000,
    output: 0.60 / 1000000
  },
  'gpt-oss-120b-medium': {
    input: 2.00 / 1000000,
    output: 8.00 / 1000000
  }
};

function calculateCost(model, inputTokens, outputTokens) {
  const price = PRICING[model];
  if (!price) {
    console.warn(`⚠️  No pricing data for model: ${model}`);
    return 0;
  }
  
  const cost = (inputTokens * price.input) + (outputTokens * price.output);
  return parseFloat(cost.toFixed(6));
}

module.exports = { PRICING, calculateCost };
