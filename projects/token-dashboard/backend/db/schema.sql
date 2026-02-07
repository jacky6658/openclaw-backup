-- OpenClaw Token Dashboard Database Schema

-- 1. Token 使用記錄
CREATE TABLE IF NOT EXISTS token_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  model VARCHAR(100) NOT NULL,
  provider VARCHAR(50) NOT NULL,
  input_tokens INTEGER DEFAULT 0,
  output_tokens INTEGER DEFAULT 0,
  total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
  event_type VARCHAR(100),
  event_description TEXT,
  session_key VARCHAR(100),
  cost_usd DECIMAL(10, 6)
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON token_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_model ON token_usage(model);
CREATE INDEX IF NOT EXISTS idx_event_type ON token_usage(event_type);

-- 2. 模型配額快照
CREATE TABLE IF NOT EXISTS model_quota (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  provider VARCHAR(50) NOT NULL,
  model VARCHAR(100) NOT NULL,
  quota_remaining_pct INTEGER,
  quota_reset_seconds INTEGER,
  auth_status VARCHAR(20),
  raw_data TEXT
);

CREATE INDEX IF NOT EXISTS idx_quota_timestamp ON model_quota(timestamp);
CREATE INDEX IF NOT EXISTS idx_quota_model ON model_quota(model);

-- 3. 事件記錄
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  event_type VARCHAR(100) NOT NULL,
  description TEXT,
  model_used VARCHAR(100),
  tokens_consumed INTEGER,
  duration_ms INTEGER,
  success BOOLEAN DEFAULT TRUE,
  metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

-- 3. 速率限制記錄
CREATE TABLE IF NOT EXISTS rate_limits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  provider VARCHAR(50) NOT NULL,
  rpm_current INTEGER,
  rpm_limit INTEGER,
  tpm_current INTEGER,
  tpm_limit INTEGER,
  cooldown_until DATETIME,
  metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_timestamp ON rate_limits(timestamp);
CREATE INDEX IF NOT EXISTS idx_rate_limits_provider ON rate_limits(provider);

-- 4. 每日摘要
CREATE TABLE IF NOT EXISTS daily_summary (
  date DATE PRIMARY KEY,
  total_tokens INTEGER,
  total_cost_usd DECIMAL(10, 4),
  by_model TEXT,
  by_event_type TEXT,
  top_consuming_events TEXT
);
