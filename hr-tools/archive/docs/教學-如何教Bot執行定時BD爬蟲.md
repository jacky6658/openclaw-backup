# 教學：如何教 Bot 執行定時 BD 爬蟲

## 🎯 目標

教會你的 AI Bot（例如 YuQi）：
1. 每 1 小時自動搜尋招聘公司
2. 爬取公司聯絡方式
3. 批量寄送 BD 合作邀請信
4. 自動回報結果到 Telegram

---

## 📚 前置知識

### 你的 Bot 需要會什麼？

1. **執行 Shell 腳本** (`exec` tool)
2. **讀取/寫入檔案** (`read`, `write` tools)
3. **建立定時任務** (`cron` tool)
4. **發送 Telegram 訊息** (`message` tool)
5. **使用 Google API** (`gog` CLI)

### 你需要準備什麼？

- ✅ OpenClaw 已安裝並運行
- ✅ Telegram Bot 已設定
- ✅ Gmail 帳號已授權（用於發信）
- ✅ Google Sheets 已授權（用於資料管理）
- ✅ BD 工具已安裝（`~/clawd/hr-tools/`）

---

## 📖 教學步驟

### Step 1: 先手動測試完整流程

在教 Bot 自動執行前，先確認所有工具都能正常運作。

#### 1.1 測試搜尋公司

```bash
cd ~/clawd/hr-tools
./bd-automation.sh search "AI工程師" 5
```

**預期結果**：
- 輸出 JSON 檔案路徑
- 包含 5 家公司的資料

**如果失敗**：檢查 `scraper-104.py` 是否存在並可執行。

---

#### 1.2 測試爬取聯絡方式

假設上一步輸出檔案是 `data/companies_20260210.json`：

```bash
./bd-automation.sh scrape data/companies_20260210.json
```

**預期結果**：
- 輸出 `data/companies_20260210_detailed.json`
- 包含公司網站、電話、Email

**如果失敗**：檢查 `agent-browser` 是否已安裝。

---

#### 1.3 測試寄信

```bash
./bd-outreach.sh preview "測試公司" "您好"
```

**預期結果**：
- 顯示 BD 信件預覽（不實際寄出）

```bash
./bd-outreach.sh send "測試公司" "your-test-email@gmail.com" "測試先生"
```

**預期結果**：
- 成功發送郵件到測試信箱
- 附件包含 Step1ne公司簡介.pdf

**如果失敗**：檢查 Gmail 授權 (`gog auth list`)。

---

#### 1.4 測試完整流程

```bash
./bd-automation.sh auto "AI工程師" 3
```

**預期結果**：
- 搜尋 3 家公司
- 爬取聯絡方式
- 整理到 Google Sheets
- 寄送 BD 信（只寄給有 Email 的公司）
- 顯示完整報告

**如果成功**：恭喜！工具已就緒，可以進入下一步。

---

### Step 2: 教 Bot 手動執行流程

在設定定時任務前，先教 Bot 如何手動執行。

#### 2.1 給 Bot 看規劃文件

在 Telegram 對 Bot 說：

```
請閱讀 /Users/user/clawd/hr-tools/CRON-BD定時任務規劃.md
```

Bot 會讀取文件並理解整個流程。

---

#### 2.2 請 Bot 執行一次

```
請執行一次 BD 客戶開發流程，使用關鍵字「AI工程師」，限制 5 家公司。
```

Bot 會：
1. 執行 `bd-automation.sh auto "AI工程師" 5`
2. 等待完成
3. 讀取結果
4. 整理成報告回覆你

**觀察 Bot 的回覆**：
- ✅ 如果成功，Bot 會告訴你找到幾家公司、寄了幾封信
- ❌ 如果失敗，Bot 會告訴你錯誤訊息

---

#### 2.3 請 Bot 回報到 Telegram 群組

```
請將剛才的 BD 結果報告發送到 Telegram 群組 -1003231629634 Topic 364
```

Bot 會使用 `message` tool 發送訊息到指定 Topic。

**確認**：到 Telegram 群組檢查是否收到訊息。

---

### Step 3: 設定定時任務

當 Bot 能成功手動執行後，就可以設定定時任務了。

#### 3.1 請 Bot 讀取 Cron 規劃

```
請閱讀 /Users/user/clawd/hr-tools/CRON-BD定時任務規劃.md 並根據規劃建立定時任務。

重要：
1. 每 1 小時執行一次
2. 使用關鍵字輪替機制（AI工程師、後端工程師、全端工程師、數據分析師、產品經理）
3. 每次限制 10 家公司
4. 結果發送到 Telegram Topic 364
5. 若無可寄信對象，靜默（HEARTBEAT_OK）
```

---

#### 3.2 Bot 會執行什麼？

Bot 會使用 `cron` tool 建立定時任務：

```javascript
cron.add({
  name: "BD 客戶開發定時爬蟲 (YQ2 HRYuqi)",
  schedule: {
    kind: "every",
    everyMs: 3600000  // 1 小時 = 3600000 毫秒
  },
  sessionTarget: "isolated",
  wakeMode: "now",
  payload: {
    kind: "agentTurn",
    message: "執行 BD 客戶開發自動化：..."
  },
  delivery: {
    mode: "announce",
    channel: "telegram",
    to: "-1003231629634/364"
  }
})
```

---

#### 3.3 確認任務已建立

```
列出所有定時任務
```

Bot 會執行 `cron list`，你應該看到：
- ✅ "BD 客戶開發定時爬蟲 (YQ2 HRYuqi)"
- ⏰ 每 1 小時執行
- 📍 下次執行時間

---

### Step 4: 監控與調整

#### 4.1 觀察首次執行

等待 1 小時後，到 Telegram Topic 364 檢查：
- ✅ Bot 是否發送了報告？
- ✅ 報告內容是否正確？
- ✅ Google Sheets 是否有新資料？

---

#### 4.2 檢查寄信狀態

登入 `aijessie88@step1ne.com` 信箱：
- 檢查「已寄郵件」資料夾
- 確認信件內容正確
- 確認附件（Step1ne公司簡介.pdf）已附上

---

#### 4.3 調整頻率（如果需要）

如果覺得 1 小時太頻繁，可以改成 2 小時：

```
請將 BD 定時任務的執行頻率改為 2 小時
```

Bot 會執行 `cron update`。

---

#### 4.4 暫停/恢復任務

暫停：
```
請暫停 BD 定時任務
```

恢復：
```
請恢復 BD 定時任務
```

---

### Step 5: 進階技巧

#### 5.1 調整關鍵字清單

編輯 `~/clawd/hr-tools/bd-automation.sh`，找到關鍵字清單：

```bash
KEYWORDS=("AI工程師" "後端工程師" "全端工程師" "數據分析師" "產品經理")
```

新增或刪除關鍵字：

```bash
KEYWORDS=("AI工程師" "後端工程師" "DevOps工程師" "前端工程師")
```

---

#### 5.2 調整每次搜尋數量

預設每次搜尋 10 家公司。如果想改成 20 家：

```
請修改 BD 定時任務，每次搜尋 20 家公司
```

Bot 會更新 Cron Job 的 `message` 內容。

---

#### 5.3 設定白名單/黑名單

如果某些公司不想寄信（例如已合作、已拒絕）：

建立檔案 `~/clawd/data/headhunter/bd_blacklist.txt`：

```
康統醫學科技
詮欣
```

修改 `bd-automation.sh`，在寄信前檢查黑名單。

---

## 🧪 測試清單

在正式啟用定時任務前，確認：

- [ ] 手動執行 `bd-automation.sh auto` 成功
- [ ] 寄信成功（檢查收件匣）
- [ ] Google Sheets 正確寫入資料
- [ ] Bot 能手動執行流程
- [ ] Bot 能發送訊息到 Telegram Topic
- [ ] Cron Job 已建立並啟用
- [ ] 第一次自動執行成功（等待 1 小時）

---

## 🐛 常見問題

### Q1: Bot 說「找不到 bd-automation.sh」

**解決方式**：
```
請確認檔案路徑，應該在 ~/clawd/hr-tools/bd-automation.sh
```

Bot 會執行 `ls -l ~/clawd/hr-tools/bd-automation.sh` 檢查。

---

### Q2: 爬蟲失敗，找不到公司

**可能原因**：
1. 104 網站結構改變
2. agent-browser 未安裝
3. 網路連線問題

**解決方式**：
```
請測試執行 ~/clawd/hr-tools/bd-automation.sh search "AI工程師" 1
並告訴我錯誤訊息
```

---

### Q3: 寄信失敗，顯示「未授權」

**解決方式**：
```
請檢查 Gmail 授權狀態，帳號 aijessie88@step1ne.com
```

Bot 會執行 `gog auth list` 並告訴你結果。

如果未授權：
```
請執行 gog auth add aijessie88@step1ne.com --services gmail
```

---

### Q4: Google Sheets 寫入失敗

**解決方式**：
```
請檢查 Google Sheets 授權，帳號 aiagentg888@gmail.com
```

如果未授權：
```
請執行 gog auth add aiagentg888@gmail.com --services sheets,drive
```

---

### Q5: Telegram 訊息發送失敗

**檢查 Topic ID**：
```
請確認 Telegram 群組 -1003231629634 是否有 Topic 364
```

如果 Topic 不存在，請在群組中建立 Topic「開發」。

---

## 📊 成效追蹤

### 每週檢查

1. **寄信數量**：本週寄了多少封信？
   ```
   請統計本週 BD 寄信數量
   ```

2. **回覆率**：收到多少家公司回覆？
   - 手動檢查 `aijessie88@step1ne.com` 信箱
   - 記錄回覆公司名單

3. **轉換率**：成功約到幾次會議/合作？
   - 手動追蹤

---

## 🎓 總結

### 你學到了什麼？

1. ✅ 如何測試 BD 工具
2. ✅ 如何教 Bot 執行 Shell 腳本
3. ✅ 如何設定定時任務
4. ✅ 如何監控和調整任務
5. ✅ 如何處理常見問題

### 下一步？

- 複製這個模式，教 Bot 其他自動化任務
- 例如：定時搜尋人選、定時跟進候選人、定時生成報表

---

## 📞 需要幫助？

如果 Bot 無法理解或執行，可以：

1. **檢查文件**：確認 `CRON-BD定時任務規劃.md` 內容完整
2. **分步執行**：不要一次給太多指令，拆成小步驟
3. **提供範例**：給 Bot 看具體的指令範例
4. **手動示範**：先手動執行一次，讓 Bot 觀察結果

---

**教學完成日期**: 2026-02-10
**作者**: YuQi (YQ2 HR YuQi)
