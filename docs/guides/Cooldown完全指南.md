# Cooldown 完全指南 - 原因、預防、處理

## 📚 目錄
1. [什麼是 Cooldown？](#什麼是-cooldown)
2. [為什麼會發生？](#為什麼會發生)
3. [各 Provider 的限制](#各-provider-的限制)
4. [如何預防？](#如何預防)
5. [發生時怎麼辦？](#發生時怎麼辦)
6. [最佳實踐](#最佳實踐)

---

## 什麼是 Cooldown？

**Cooldown（冷卻期）= Rate Limit（速率限制）觸發後的禁用期**

當你短時間內發送太多請求，AI 提供商會：
1. 拒絕你的新請求
2. 強制你等待一段時間（cooldown period）
3. 等待時間結束後才能繼續使用

**典型錯誤訊息**：
```
Provider anthropic is in cooldown (all profiles unavailable) (rate_limit)
```

---

## 為什麼會發生？

### 🎯 核心概念：RPM 和 TPM

所有 AI API 都有兩種主要限制：

#### 1. **RPM (Requests Per Minute)** - 每分鐘請求數
- **定義**：1 分鐘內最多可以發送幾次請求
- **例子**：Anthropic 限制 ~50 RPM
- **觸發**：1 分鐘內發送超過 50 個訊息 → Cooldown

#### 2. **TPM (Tokens Per Minute)** - 每分鐘 Token 數
- **定義**：1 分鐘內最多可以處理多少 tokens
- **例子**：Anthropic 限制 ~100,000 TPM
- **觸發**：1 分鐘內處理超過 100k tokens → Cooldown

### 🔥 常見觸發情況

| 情況 | 原因 | 解決方法 |
|------|------|---------|
| **連續快速發送訊息** | RPM 超限 | 間隔 5-10 秒再發 |
| **一次讀取大量檔案** | TPM 超限 | 分批讀取 |
| **生成超長內容** | TPM 超限 | 限制輸出長度 |
| **多個應用共用 token** | RPM/TPM 累加超限 | 使用獨立 token |
| **Context 太大** | 單次請求 token 過多 | 開啟 compaction |

---

## 各 Provider 的限制

### 📊 主要 Provider 對比

| Provider | RPM 限制 | TPM 限制 | Cooldown 機制 | 備註 |
|----------|---------|---------|--------------|------|
| **Anthropic API** | ~50 | ~100k | 15-60 分鐘 | 嚴格 |
| **Google Antigravity** | N/A | 滾動視窗配額 | 5 小時重置 | 較寬鬆 |
| **Google Gemini CLI** | ~60 | N/A | 罕見 | 非常寬鬆 |
| **OpenAI Codex** | ~100 | ~200k | 雙重配額 | 5h + Day |

---

### 詳細說明

#### 1. **Anthropic API**（最常 Cooldown）
```
限制：
- RPM: 50 requests/min
- TPM: 100,000 tokens/min

Cooldown 時長：
- 輕微超限：15 分鐘
- 嚴重超限：60 分鐘

特點：
- 非常嚴格
- 多個 profile 共用限制（同一個 API key）
- 建議：避免連發，設置 fallback
```

#### 2. **Google Antigravity**（推薦）
```
限制：
- 無 RPM/TPM（改用滾動視窗配額）
- 5 小時內可用的配額（用完重置）

Cooldown 時長：
- 配額用完後等待重置（最多 5 小時）

特點：
- 較少 cooldown
- 接 Claude Pro/Max 帳號
- 建議：主力使用
```

#### 3. **Google Gemini CLI**（備用首選）
```
限制：
- RPM: ~60 requests/min
- 無明顯 TPM 限制

Cooldown 時長：
- 幾乎不會 cooldown

特點：
- 非常寬鬆
- 適合大量請求
- 建議：當 Claude cooldown 時切換
```

#### 4. **OpenAI Codex**
```
限制：
- 雙重配額：5h quota + Day quota
- RPM: ~100 requests/min
- TPM: ~200,000 tokens/min

Cooldown 時長：
- 5h quota: 每 5 小時重置
- Day quota: 每天重置

特點：
- Day quota 容易耗盡
- 建議：短時間內使用
```

---

## 如何預防？

### ✅ 方法 1：控制請求頻率（最重要）

**避免連續發送**：
```
❌ 錯誤做法：
發送訊息 1
立刻發送訊息 2
立刻發送訊息 3
→ 觸發 RPM 限制

✅ 正確做法：
發送訊息 1
等待回覆
發送訊息 2
等待回覆
→ 不會觸發
```

**建議間隔**：
- Anthropic API：至少間隔 **5 秒**
- 其他 Provider：至少間隔 **2 秒**

---

### ✅ 方法 2：控制 Token 使用量

#### 減少 Context 大小
```json
{
  "compaction": {
    "mode": "safeguard"  // 自動壓縮歷史對話
  }
}
```

#### 分批讀取檔案
```
❌ 一次讀取 10 個大檔案 → TPM 爆表
✅ 每次讀 2-3 個 → 安全
```

#### 限制輸出長度
```
❌ 「寫一篇 5000 字的文章」→ 單次 token 過多
✅ 「寫 500 字摘要」→ 分段處理
```

---

### ✅ 方法 3：設置 Fallback 機制

**推薦配置**：
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "google-antigravity/claude-opus-4-5-thinking",
        "fallbacks": [
          "google-gemini-cli/gemini-2.5-pro",
          "anthropic/claude-sonnet-4-5"
        ]
      }
    }
  }
}
```

**效果**：
1. 主力用 Antigravity（較少 cooldown）
2. Antigravity cooldown → 自動切 Gemini
3. Gemini 不可用 → 切 Anthropic API

---

### ✅ 方法 4：監控用量（Token Dashboard）

**即將推出的功能**：
- 即時顯示 RPM/TPM 使用率
- 接近限制時自動預警
- 建議切換時機

---

## 發生時怎麼辦？

### 🚨 立即處理 SOP

#### Step 1：切換到可用模型
```
/model gemini-2.5-pro
```

#### Step 2：等待 10 秒
（模型切換需要時間）

#### Step 3：測試
```
hi
```

#### Step 4：確認恢復
看到正常回覆 → ✅ 完成

---

### 🔍 診斷 Cooldown 原因

```bash
# 查看所有模型狀態
openclaw models

# 輸出範例：
- anthropic:default [cooldown 55m]  ← 這個在 cooldown
- google-antigravity ok             ← 這個可用
```

---

### ⏰ Cooldown 時長參考

| 情況 | 時長 | 處理方式 |
|------|------|---------|
| 輕微超限 | 5-15 分鐘 | 切換模型，短暫等待 |
| 中度超限 | 30-60 分鐘 | 切換模型，長時間使用其他 |
| 嚴重超限 | 1-2 小時 | 檢查是否有異常使用 |

---

## 最佳實踐

### 🎯 推薦設定

#### 1. **主力模型選擇**
```
首選：google-antigravity/claude-opus-4-5-thinking
原因：
- 用 Claude Max 配額（不易 cooldown）
- 5 小時滾動視窗（較寬鬆）
- 品質最好
```

#### 2. **Fallback 順序**
```
第一備用：google-gemini-cli/gemini-2.5-pro
原因：幾乎不會 cooldown，可長時間使用

第二備用：anthropic/claude-sonnet-4-5
原因：cooldown 解除後品質好
```

#### 3. **使用習慣**
```
✅ 每次發送訊息間隔 5 秒以上
✅ 大任務拆成多個小任務
✅ 定期檢查 /models 確認配額
✅ 開啟 compaction 壓縮 context
❌ 避免連續快速發送
❌ 避免一次處理大量檔案
```

---

### 📊 Token Dashboard 監控（計劃中）

**即將推出**：
- **RPM 監控**：顯示當前 RPM 使用率（12/50）
- **TPM 監控**：顯示當前 TPM 使用率（45k/100k）
- **Cooldown 倒數**：顯示各 Provider 的 cooldown 剩餘時間
- **自動切換**：接近限制時自動切換模型
- **Telegram 通知**：cooldown 時發送提醒

---

## 快速參考卡

### 🆘 緊急指令

```bash
# 查看所有模型狀態
/models

# 切換到 Gemini（最穩定）
/model gemini-2.5-pro

# 切換到 Antigravity（用 Claude Max）
/model google-antigravity/claude-opus-4-5-thinking

# 切回預設
/model default

# 查看當前狀態
/status
```

---

### 📋 Cooldown 檢查清單

當遇到 cooldown 時，檢查：
- [ ] 是否連續快速發送了訊息？
- [ ] 是否一次讀取了大量檔案？
- [ ] 是否有其他應用使用同一個 token？
- [ ] Context 是否過大（需要 compaction）？
- [ ] 是否可以切換到其他模型？

---

## 相關文件

- [緊急切換模型指南](./緊急切換模型指南.md)
- [Token Dashboard 設計](../projects/token-dashboard/DESIGN.md)
- [OpenClaw 終端機指令大全](./OpenClaw-終端機指令大全.md)

---

**最後更新**：2026-02-06  
**版本**：1.0
