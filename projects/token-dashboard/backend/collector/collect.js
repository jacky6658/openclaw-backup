#!/usr/bin/env node

/**
 * Data Collector - 收集 OpenClaw token 用量和模型狀態
 * 執行：node backend/collector/collect.js
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const execAsync = promisify(exec);
const DB_PATH = path.join(__dirname, '../db/openclaw-tokens.db');

// 執行 shell 指令
async function runCommand(cmd) {
  try {
    const { stdout } = await execAsync(cmd);
    return stdout.trim();
  } catch (error) {
    console.error(`Command failed: ${cmd}`, error.message);
    return null;
  }
}

// 解析 openclaw models 輸出
function parseModelsOutput(output) {
  const providers = {};
  const lines = output.split('\n');
  
  let currentProvider = null;
  
  for (const line of lines) {
    // 解析 provider 用量行
    // 例：- google-antigravity usage: claude-sonnet-4-5 60% left ⏱6d 23h
    const providerMatch = line.match(/^- (\S+) usage: (.+)$/);
    if (providerMatch) {
      currentProvider = providerMatch[1];
      providers[currentProvider] = {
        models: [],
        raw: providerMatch[2]
      };
      
      // 解析模型配額
      const modelParts = providerMatch[2].split('·');
      for (const part of modelParts) {
        const modelMatch = part.trim().match(/^(\S+)\s+(\d+)%\s+left(?:\s+⏱(.+))?$/);
        if (modelMatch) {
          providers[currentProvider].models.push({
            name: modelMatch[1],
            quota_left: parseInt(modelMatch[2]),
            reset_time: modelMatch[3] || null
          });
        }
      }
    }
    
    // 解析 cooldown 狀態
    // 例：- anthropic:default [cooldown 55m]
    const cooldownMatch = line.match(/- (\S+):(\S+).*\[cooldown\s+(.+)\]/);
    if (cooldownMatch) {
      const provider = cooldownMatch[1];
      const profile = cooldownMatch[2];
      const cooldownTime = cooldownMatch[3];
      
      if (!providers[provider]) {
        providers[provider] = { models: [], cooldown: [] };
      }
      if (!providers[provider].cooldown) {
        providers[provider].cooldown = [];
      }
      providers[provider].cooldown.push({
        profile,
        time: cooldownTime
      });
    }
  }
  
  return providers;
}

// 解析 session_status JSON 輸出
function parseSessionStatus(output) {
  try {
    // 移除 ANSI 顏色碼和其他特殊字符
    const cleaned = output.replace(/\x1B\[[0-9;]*[a-zA-Z]/g, '');
    
    // 提取 JSON 部分（如果有）
    const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    
    // 手動解析純文本輸出
    const result = {};
    const lines = cleaned.split('\n');
    
    for (const line of lines) {
      if (line.includes('Model:')) {
        result.model = line.split('Model:')[1].trim().split('·')[0].trim();
      }
      if (line.includes('Tokens:')) {
        const tokensMatch = line.match(/(\d+)\s+in\s+\/\s+(\d+)\s+out/);
        if (tokensMatch) {
          result.tokens_in = parseInt(tokensMatch[1]);
          result.tokens_out = parseInt(tokensMatch[2]);
        }
      }
      if (line.includes('Context:')) {
        const contextMatch = line.match(/(\d+[kKmM]?)\/(\d+[kKmM]?)/);
        if (contextMatch) {
          result.context_used = contextMatch[1];
          result.context_total = contextMatch[2];
        }
      }
    }
    
    return result;
  } catch (error) {
    console.error('Failed to parse session status:', error.message);
    return null;
  }
}

// 儲存 token 用量到資料庫
async function saveTokenUsage(db, data) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO token_usage (model, provider, input_tokens, output_tokens)
      VALUES (?, ?, ?, ?)
    `);
    
    stmt.run(
      data.model || 'unknown',
      data.provider || 'unknown',
      data.tokens_in || 0,
      data.tokens_out || 0
    );
    
    stmt.finalize((err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

// 儲存模型配額到資料庫
async function saveModelQuota(db, provider, modelData) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO model_quota (provider, model, quota_remaining_pct, raw_data)
      VALUES (?, ?, ?, ?)
    `);
    
    stmt.run(
      provider,
      modelData.name,
      modelData.quota_left,
      JSON.stringify(modelData)
    );
    
    stmt.finalize((err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

// 儲存 Rate Limit 資料
async function saveRateLimit(db, provider, data) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO rate_limits (provider, cooldown_until, metadata)
      VALUES (?, ?, ?)
    `);
    
    stmt.run(
      provider,
      data.cooldown_until || null,
      JSON.stringify(data)
    );
    
    stmt.finalize((err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

// 主函數
async function collect() {
  console.log('🔍 Collecting OpenClaw token usage...');
  
  const db = new sqlite3.Database(DB_PATH);
  
  try {
    // 1. 收集 session_status
    console.log('📊 Running: openclaw session_status...');
    const sessionOutput = await runCommand('openclaw session_status 2>&1');
    const sessionData = parseSessionStatus(sessionOutput);
    
    if (sessionData && sessionData.model) {
      await saveTokenUsage(db, sessionData);
      console.log(`✅ Saved token usage: ${sessionData.tokens_in} in / ${sessionData.tokens_out} out`);
    }
    
    // 2. 收集 openclaw models
    console.log('📊 Running: openclaw models...');
    const modelsOutput = await runCommand('openclaw models 2>&1');
    const providers = parseModelsOutput(modelsOutput);
    
    // 儲存模型配額
    for (const [provider, data] of Object.entries(providers)) {
      if (data.models && data.models.length > 0) {
        for (const model of data.models) {
          await saveModelQuota(db, provider, model);
          console.log(`✅ Saved quota: ${provider}/${model.name} - ${model.quota_left}%`);
        }
      }
      
      // 儲存 cooldown 資料
      if (data.cooldown && data.cooldown.length > 0) {
        await saveRateLimit(db, provider, { cooldown: data.cooldown });
        console.log(`⚠️ Cooldown detected: ${provider}`);
      }
    }
    
    console.log('✅ Data collection completed!');
    
  } catch (error) {
    console.error('❌ Collection failed:', error);
  } finally {
    db.close();
  }
}

// 執行
if (require.main === module) {
  collect().catch(console.error);
}

module.exports = { collect, parseModelsOutput, parseSessionStatus };
