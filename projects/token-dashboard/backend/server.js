#!/usr/bin/env node

/**
 * Token Dashboard - REST API Server
 * 啟動：node backend/server.js
 * 訪問：http://localhost:3737
 */

const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const { promisify } = require('util');
const { calculateCost } = require('./utils/pricing');

const execAsync = promisify(exec);
const app = express();
const PORT = process.env.PORT || 3737;
const DB_PATH = path.join(__dirname, 'db/openclaw-tokens.db');
const OPENCLAW_CONFIG_PATH = path.join(require('os').homedir(), '.openclaw/openclaw.json');

// 中間件
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// 資料庫連線
function getDb() {
  return new sqlite3.Database(DB_PATH);
}

// API: 總覽統計
app.get('/api/overview', (req, res) => {
  const db = getDb();
  const { period = 'today' } = req.query;
  
  let timeFilter = '';
  switch (period) {
    case 'today':
      timeFilter = "AND date(timestamp) = date('now')";
      break;
    case 'week':
      timeFilter = "AND timestamp >= datetime('now', '-7 days')";
      break;
    case 'month':
      timeFilter = "AND timestamp >= datetime('now', '-30 days')";
      break;
  }
  
  db.get(`
    SELECT 
      SUM(input_tokens) as total_tokens_in,
      SUM(output_tokens) as total_tokens_out,
      COUNT(*) as total_requests,
      GROUP_CONCAT(DISTINCT model) as models_used
    FROM token_usage
    WHERE 1=1 ${timeFilter}
  `, (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    const totalTokens = (row.total_tokens_in || 0) + (row.total_tokens_out || 0);
    const cost = calculateCost('claude-sonnet-4-5', row.total_tokens_in || 0, row.total_tokens_out || 0);
    
    res.json({
      period,
      total_tokens: totalTokens,
      total_tokens_in: row.total_tokens_in || 0,
      total_tokens_out: row.total_tokens_out || 0,
      total_requests: row.total_requests || 0,
      estimated_cost: cost,
      models_used: row.models_used ? row.models_used.split(',') : []
    });
  });
  
  db.close();
});

// API: 模型配額狀態（從資料庫讀取 - 正確欄位名）
app.get('/api/models', async (req, res) => {
  try {
    const db = getDb();
    
    // 從資料庫讀取最新的模型配額
    db.all(`
      SELECT 
        provider,
        model,
        quota_remaining_pct as quota_left,
        100 as quota_limit,
        quota_reset_seconds as cooldown_seconds,
        timestamp
      FROM model_quota
      WHERE timestamp >= datetime('now', '-10 minutes')
      ORDER BY timestamp DESC
    `, (err, rows) => {
      if (err) {
        console.error('查詢資料庫失敗:', err);
        res.json({ models: [] });
        db.close();
        return;
      }
      
      const models = rows.map(row => ({
        provider: row.provider,
        model: row.model,
        full_name: `${row.provider}/${row.model}`,
        quota_left: row.quota_left || 50,
        quota_limit: row.quota_limit || 100,
        cooldown_seconds: row.cooldown_seconds || 0,
        status: (row.cooldown_seconds && row.cooldown_seconds > 0) ? 'cooldown' : 'ok'
      }));
      
      res.json({ models });
      db.close();
    });
  } catch (error) {
    console.error('獲取模型列表失敗:', error);
    res.status(500).json({ error: error.message, models: [] });
  }
});

// API: Rate Limits 狀態
app.get('/api/rate-limits', (req, res) => {
  const db = getDb();
  
  // 取得最新的 rate limit 記錄
  db.all(`
    SELECT 
      rl1.provider,
      rl1.rpm_current,
      rl1.rpm_limit,
      rl1.tpm_current,
      rl1.tpm_limit,
      rl1.cooldown_until,
      rl1.timestamp,
      rl1.metadata
    FROM rate_limits rl1
    INNER JOIN (
      SELECT provider, MAX(timestamp) as max_timestamp
      FROM rate_limits
      GROUP BY provider
    ) rl2
    ON rl1.provider = rl2.provider 
    AND rl1.timestamp = rl2.max_timestamp
    ORDER BY rl1.provider
  `, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    res.json({
      rate_limits: rows.map(row => ({
        provider: row.provider,
        rpm: row.rpm_current ? `${row.rpm_current}/${row.rpm_limit}` : 'N/A',
        tpm: row.tpm_current ? `${row.tpm_current}/${row.tpm_limit}` : 'N/A',
        cooldown_until: row.cooldown_until,
        timestamp: row.timestamp,
        metadata: row.metadata ? JSON.parse(row.metadata) : {}
      }))
    });
  });
  
  db.close();
});

// API: 歷史趨勢
app.get('/api/history', (req, res) => {
  const db = getDb();
  const { days = 7 } = req.query;
  
  db.all(`
    SELECT 
      date(timestamp) as date,
      SUM(input_tokens) as total_tokens_in,
      SUM(output_tokens) as total_tokens_out,
      COUNT(*) as requests
    FROM token_usage
    WHERE timestamp >= datetime('now', '-${parseInt(days)} days')
    GROUP BY date(timestamp)
    ORDER BY date DESC
  `, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    const history = rows.map(row => ({
      date: row.date,
      total_tokens: (row.total_tokens_in || 0) + (row.total_tokens_out || 0),
      tokens_in: row.total_tokens_in || 0,
      tokens_out: row.total_tokens_out || 0,
      requests: row.requests || 0
    }));
    
    res.json({ history });
  });
  
  db.close();
});

// API: 成本估算
app.get('/api/cost', (req, res) => {
  const db = getDb();
  const { period = 'month' } = req.query;
  
  let timeFilter = '';
  switch (period) {
    case 'today':
      timeFilter = "AND date(timestamp) = date('now')";
      break;
    case 'week':
      timeFilter = "AND timestamp >= datetime('now', '-7 days')";
      break;
    case 'month':
      timeFilter = "AND timestamp >= datetime('now', '-30 days')";
      break;
  }
  
  db.all(`
    SELECT 
      model,
      SUM(input_tokens) as total_tokens_in,
      SUM(output_tokens) as total_tokens_out
    FROM token_usage
    WHERE 1=1 ${timeFilter}
    GROUP BY model
  `, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    let totalCost = 0;
    const breakdown = rows.map(row => {
      const cost = calculateCost(row.model, row.total_tokens_in || 0, row.total_tokens_out || 0);
      totalCost += cost;
      
      return {
        model: row.model,
        tokens_in: row.total_tokens_in || 0,
        tokens_out: row.total_tokens_out || 0,
        cost: cost.toFixed(4)
      };
    });
    
    res.json({
      period,
      total_cost: totalCost.toFixed(4),
      breakdown
    });
  });
  
  db.close();
});

// API: 獲取當前配置（優化版 - 避免卡住）
app.get('/api/config', async (req, res) => {
  try {
    // 讀取 openclaw.json
    let config = {};
    let currentModel = 'unknown';
    let quotaRemaining = 50; // 默認值
    
    if (fs.existsSync(OPENCLAW_CONFIG_PATH)) {
      try {
        const configContent = fs.readFileSync(OPENCLAW_CONFIG_PATH, 'utf8');
        config = JSON.parse(configContent);
        currentModel = config.llm?.defaultProfile?.primary || 'unknown';
      } catch (e) {
        console.error('讀取配置文件失敗:', e.message);
      }
    }
    
    // 檢查 Gateway 狀態（快速方法）
    let gatewayRunning = false;
    try {
      const { stdout } = await execAsync('pgrep -f "openclaw-gateway" | head -1', { timeout: 1000 });
      gatewayRunning = stdout.trim() !== '';
    } catch (e) {
      gatewayRunning = false;
    }
    
    // 檢查警告
    const warnings = [];
    if (!gatewayRunning) {
      warnings.push('Gateway 未運行');
    }
    
    res.json({
      current_model: currentModel,
      gateway_running: gatewayRunning,
      quota_remaining: quotaRemaining,
      warnings: warnings,
      config: {}  // 不返回完整配置，減少數據量
    });
  } catch (error) {
    console.error('獲取配置失敗:', error);
    res.status(500).json({ error: error.message });
  }
});

// API: 切換模型
app.post('/api/switch-model', async (req, res) => {
  try {
    const { model } = req.body;
    
    if (!model) {
      return res.status(400).json({ error: '未提供模型名稱' });
    }
    
    // 讀取當前配置
    if (!fs.existsSync(OPENCLAW_CONFIG_PATH)) {
      return res.status(404).json({ error: 'OpenClaw 配置文件不存在' });
    }
    
    const configContent = fs.readFileSync(OPENCLAW_CONFIG_PATH, 'utf8');
    const config = JSON.parse(configContent);
    
    // 更新 primary 模型
    if (!config.llm) config.llm = {};
    if (!config.llm.defaultProfile) config.llm.defaultProfile = {};
    
    config.llm.defaultProfile.primary = model;
    
    // 寫回配置文件
    fs.writeFileSync(OPENCLAW_CONFIG_PATH, JSON.stringify(config, null, 2), 'utf8');
    
    // 重啟 Gateway
    try {
      await execAsync('openclaw gateway stop');
      await new Promise(resolve => setTimeout(resolve, 1000)); // 等待 1 秒
      await execAsync('openclaw gateway start');
    } catch (e) {
      console.warn('Gateway 重啟警告:', e.message);
    }
    
    res.json({ 
      success: true, 
      message: `已切換到 ${model}`,
      new_model: model
    });
  } catch (error) {
    console.error('切換模型失敗:', error);
    res.status(500).json({ error: error.message });
  }
});

// API: 配額詳情（實時執行 openclaw models）
app.get('/api/quota-status', async (req, res) => {
  try {
    const { stdout } = await execAsync('openclaw models --json 2>/dev/null || openclaw models');
    
    // 嘗試解析 JSON 輸出（如果支持）
    let providers = {};
    
    try {
      const jsonData = JSON.parse(stdout);
      
      // 提取 OAuth/token status 部分
      if (jsonData['oauth_token_status']) {
        Object.entries(jsonData['oauth_token_status']).forEach(([providerKey, profiles]) => {
          profiles.forEach(profile => {
            if (!providers[providerKey]) {
              providers[providerKey] = [];
            }
            
            providers[providerKey].push({
              profile: profile.profile || profile.name,
              status: profile.status === 'ok' ? 'ok' : 'expired',
              full_name: `${providerKey}/${profile.profile}`
            });
          });
        });
      }
    } catch (e) {
      // Fallback: 手動解析文本輸出
      const lines = stdout.split('\n');
      
      // 查找 "OAuth/token status" 部分
      let inOAuthSection = false;
      let currentProvider = null;
      
      lines.forEach(line => {
        if (line.includes('OAuth/token status')) {
          inOAuthSection = true;
          return;
        }
        
        if (!inOAuthSection) return;
        
        // 匹配 Provider 行：「- provider」
        if (line.match(/^- ([\w-]+)$/)) {
          currentProvider = line.match(/^- ([\w-]+)$/)[1];
          if (!providers[currentProvider]) {
            providers[currentProvider] = [];
          }
          return;
        }
        
        // 匹配內容行：「  - profile_name ... status」
        const profileMatch = line.match(/^\s+-\s+([\w:.-]+)\s+(.+)$/);
        if (profileMatch && currentProvider) {
          const [, profileName, details] = profileMatch;
          providers[currentProvider].push({
            profile: profileName,
            status: details.includes('ok') ? 'ok' : 'expired',
            details: details,
            full_name: `${currentProvider}/${profileName}`
          });
        }
      });
    }
    
    res.json({
      providers,
      timestamp: new Date().toISOString(),
      raw_output: stdout.substring(0, 2000) // 限制輸出大小
    });
  } catch (error) {
    console.error('執行 openclaw models 失敗:', error);
    res.status(500).json({ error: error.message });
  }
});

// 健康檢查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 啟動伺服器
app.listen(PORT, () => {
  console.log(`🚀 Token Dashboard running at http://localhost:${PORT}`);
  console.log(`📊 API endpoints:`);
  console.log(`   - GET /api/overview?period=today|week|month`);
  console.log(`   - GET /api/models`);
  console.log(`   - GET /api/rate-limits`);
  console.log(`   - GET /api/history?days=7`);
  console.log(`   - GET /api/cost?period=today|week|month`);
  console.log(`   - GET /api/health`);
});

module.exports = app;
