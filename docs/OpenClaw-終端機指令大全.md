# OpenClaw 終端機指令大全（Cheat Sheet）

> 適用版本：OpenClaw 2026.2.x（你目前 CLI 顯示 2026.2.1）
> 
> 目的：把「常用 + 可能會用到」的指令整理成一份，遇到狀況直接照貼就能跑。

---

## 0) 先記 3 個最常用

```bash
openclaw status
openclaw dashboard
openclaw logs --follow
```

---

## 1) 安裝 / 初始化 / 新手上線

### 安裝（macOS / Windows / Linux 共用）
```bash
npm install -g openclaw
openclaw --version
```

### 初始化（建立 ~/.openclaw/openclaw.json + workspace）
```bash
openclaw setup
```

### 一條龍新手導引（推薦）
```bash
openclaw onboard
openclaw configure
```

---

## 2) 狀態檢查（你卡關先跑這個）

### 快速總覽
```bash
openclaw status
```

### 全量可貼給別人排查（read-only）
```bash
openclaw status --all
```

### 深度探測（會 probe 各 channel）
```bash
openclaw status --deep
```

### JSON 輸出（給自動化/工具用）
```bash
openclaw status --json
```

---

## 3) 打開 Dashboard（Control UI）

### 最快（會印出 + 複製 tokenized link，並嘗試自動打開）
```bash
openclaw dashboard
```

### 只印出 URL，不自動開瀏覽器
```bash
openclaw dashboard --no-open
```

---

## 4) Config 設定（最常改這邊）

> OpenClaw 的主要設定檔通常在：`~/.openclaw/openclaw.json`

### 讀取某個設定值
```bash
openclaw config get <dot.path>
# 例：
openclaw config get gateway.mode
openclaw config get channels.telegram.botToken
```

### 設定某個值
```bash
openclaw config set <dot.path> <value>
# 例：
openclaw config set gateway.mode local
openclaw config set channels.telegram.botToken "<YOUR_TELEGRAM_BOT_TOKEN>"
```

### 移除某個設定
```bash
openclaw config unset <dot.path>
```

### 互動式設定精靈
```bash
openclaw config
openclaw config --section web
openclaw config --section models
```

---

## 5) Gateway（啟動 / 重啟 / 狀態 / 連線）

### 服務狀態
```bash
openclaw gateway status
```

### 安裝 / 移除後台服務（launchd/systemd/排程）
```bash
openclaw gateway install
openclaw gateway uninstall
```

### 啟動 / 停止 / 重啟服務
```bash
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
```

### 前台直接跑（除錯用）
```bash
openclaw gateway run --verbose
```

### 強制殺掉佔用 port 再啟動
```bash
openclaw gateway run --force
```

### Discover / Probe
```bash
openclaw gateway discover
openclaw gateway probe
openclaw gateway health
```

---

## 6) Logs（排錯必看）

### 看最近 200 行
```bash
openclaw logs
```

### 追 log（一直跟著跑）
```bash
openclaw logs --follow
```

### 指定更多行數
```bash
openclaw logs --limit 500
```

### JSON / plain
```bash
openclaw logs --json
openclaw logs --plain
```

---

## 7) Doctor（自動修復常見問題）

### 健康檢查 + 建議
```bash
openclaw doctor
```

### 直接修（常用）
```bash
openclaw doctor --fix
# or
openclaw doctor --repair
```

### 直接產生/配置 gateway token（需要時）
```bash
openclaw doctor --generate-gateway-token
```

---

## 8) Telegram / Channels 管理

### 列出目前有哪些 channel
```bash
openclaw channels list
```

### channel 狀態
```bash
openclaw channels status
```

### 查能力（支援哪些功能）
```bash
openclaw channels capabilities
```

### resolve 名稱→ID（群組/使用者/頻道）
```bash
openclaw channels resolve --help
```

> Telegram 設定常用（新版路徑）：
```bash
openclaw config set channels.telegram.botToken "<TOKEN>"
```

---

## 9) 發訊息（CLI 直接送）

> 主要用於測試或自動化；正式流程通常由 Agent 透過工具發。

### 送文字
```bash
openclaw message send --channel telegram --target <chatIdOrName> --message "Hi"
```

### 送檔案
```bash
openclaw message send --channel telegram --target <chatIdOrName> --media ./file.pdf
```

### 反應 / 編輯 / 刪除（視 channel 支援）
```bash
openclaw message react --help
openclaw message edit --help
openclaw message delete --help
```

---

## 10) Sessions（列出對話 session）

```bash
openclaw sessions
openclaw sessions --active 120
openclaw sessions --json
```

---

## 11) Memory（重建索引 / 搜尋）

```bash
openclaw memory status
openclaw memory index
openclaw memory search --help
```

---

## 12) Cron（排程任務）

```bash
openclaw cron status
openclaw cron list
openclaw cron add --help
openclaw cron runs --help
openclaw cron run --help
```

---

## 13) Skills / Plugins（擴充能力）

### Skills
```bash
openclaw skills list
openclaw skills info <skillName>
openclaw skills check
```

### Plugins
```bash
openclaw plugins list
openclaw plugins info <pluginName>
openclaw plugins enable <pluginName>
openclaw plugins disable <pluginName>
openclaw plugins install <npmSpecOrPath>
openclaw plugins update
openclaw plugins doctor
```

---

## 14) Security（安全檢查）

```bash
openclaw security audit
```

---

## 15) 更新 / 重置 / 解除安裝

### 更新 CLI（只有你要更新時才用）
```bash
openclaw update
```

### reset（保留 CLI，本機狀態重置）
```bash
openclaw reset
```

### uninstall（移除 gateway service + local data，CLI 留著）
```bash
openclaw uninstall
```

---

## 16) 常用排錯 SOP（我建議你收藏這段）

```bash
openclaw status --all
openclaw doctor --fix
openclaw gateway restart
openclaw dashboard
openclaw logs --follow
```

---

## 17) 小抄：常見 dot.path（你會常改）

- `gateway.mode`
- `gateway.bind`
- `gateway.auth.mode`
- `gateway.auth.token`
- `channels.telegram.botToken`
- `models.*` / `openai.apiKey` / `anthropic.apiKey` / `google.apiKey`（依你設定而定）

---

> 註：每個子命令都有 `--help`，忘了用法就：
```bash
openclaw <command> --help
```
