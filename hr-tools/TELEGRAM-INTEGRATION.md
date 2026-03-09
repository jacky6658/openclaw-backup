# Telegram 群組整合指南
**群組**：HR AI招募自動化 (`-1003231629634`)  
**目的**：將 AI 招聘系統整合到現有 Telegram workflow

---

## 📋 整合方案概覽

### 現有 Topics 分工

| Topic | 用途 | 現有功能 | 新增功能 |
|-------|------|----------|----------|
| **Topic 4** | #1履歷進件 | 履歷自動歸檔 | - |
| **Topic 304** | #2履歷池 | 履歷搜尋、狀態更新 | **AI 配對、穩定性評分** ✨ |
| **Topic 319** | #2JD列表 | 職缺管理 | **文化問卷、JD 解析** ✨ |
| **Topic 326** | 總覽看板 | Pipeline 視覺化 | **配對結果展示** ✨ |
| **Topic 364** | #BD開發 | 客戶開發 | - |

---

## 🎯 使用場景設計

### 場景 1：新職缺開案（Topic 319）

#### 步驟流程
```
用戶 → Topic 319 發送：
「@YuQi 新職缺：AI工程師」

YuQi 自動回覆：
「收到！請填寫職缺資訊：

方法 A（快速）：貼上 JD 文字，我幫你解析
方法 B（精準）：填寫需求問卷（10 題，5 分鐘）
方法 C（完整）：JD + 公司文化問卷

請選擇：A / B / C」
```

#### 選擇 A - JD 文字解析
```
用戶：A
用戶：[貼上 JD 文字]

YuQi：
「✅ JD 解析完成！

📋 職位：AI工程師
🎯 必備技能：Python, Machine Learning, AI
💼 年資要求：3+ 年
💰 薪資範圍：80k-120k
📍 地點：台北

已新增至職缺管理表（行 15）
開始搜尋候選人？（Y/N）」
```

#### 選擇 B - 需求問卷
```
用戶：B

YuQi：
「📝 請填寫需求問卷：
https://forms.gle/[問卷連結]

填完後回傳「完成」，我會自動抓取資料」

用戶：完成

YuQi：
「✅ 問卷已接收！

📋 職位：AI工程師
🎯 團隊規模：10 人
⏰ 急迫性：1 個月內
💡 特殊要求：需有 TensorFlow 經驗

已新增至職缺管理表（行 15）
開始搜尋候選人？（Y/N）」
```

#### 選擇 C - JD + 公司文化
```
用戶：C

YuQi：
「📝 步驟 1：貼上 JD 文字」

用戶：[貼上 JD]

YuQi：
「✅ JD 解析完成！

📝 步驟 2：填寫公司文化問卷
https://forms.gle/[公司文化問卷]

填完後回傳「完成」」

用戶：完成

YuQi：
「✅ 公司文化已接收！

🏢 工作節奏：快速迭代
⏰ 加班文化：經常加班
⚖️ WLB：工作優先

搜尋時將優先推薦文化適配的候選人
開始搜尋？（Y/N）」
```

---

### 場景 2：搜尋候選人（Topic 304）

#### 自動搜尋（從場景 1 觸發）
```
用戶：Y

YuQi：
「🔍 開始搜尋候選人...

搜尋管道：
✅ GitHub（技術人才）
✅ LinkedIn（專業人才）
⏸️ 履歷池（內部候選人）

預計 2-3 分鐘完成」

[2 分鐘後]

YuQi @ Topic 304：
「✅ AI工程師 - 搜尋完成！

找到 25 位候選人：
📊 AI 配對結果：
• P0（高度匹配）：5 位 ✨
• P1（匹配）：12 位
• P2（需確認）：8 位

Top 5 推薦（P0）：
1. 張大明 - 90.5 分（穩定性 A，文化適配 85）
   GitHub: github.com/zhangdaming
   
2. 李小華 - 87.3 分（穩定性 B，文化適配 90）
   LinkedIn: linkedin.com/in/lixiaohua
   
3. ...

完整清單已匯入履歷池（行 156-180）
要查看詳細報告？回覆「報告 AI工程師」」
```

#### 手動搜尋
```
用戶 @ Topic 304：
「@YuQi 搜尋 AI工程師」

YuQi：
「🔍 開始搜尋 AI工程師...
（後續同上）」
```

---

### 場景 3：查看候選人詳細資料（Topic 304）

```
用戶 @ Topic 304：
「@YuQi 候選人詳情 張大明」

YuQi：
「👤 候選人：張大明

📊 綜合評分：90.5/100（P0 - 高度匹配）

🎯 配對細節：
• 技能匹配：28/30（Python, ML, AI 全符合）
• 工作經驗：18/20（8.7 年，超出要求 5.7 年）
• 產業相關：10/10（科技產業）
• 穩定性：27/30（90 分，A 級）
• 加分項：7/10（GitHub 120 stars）

💼 職涯穩定性：90/100（A 級 - 極低風險）
  • 總年資：8.7 年
  • 跳槽次數：2 次（平均 3.5 年/份工作）
  • 目前在職：24 個月（穩定）

🏢 文化適配：85/100（高度適配）
  • 工作節奏：✅ 適應快速變化
  • 加班接受度：✅ 可以接受
  • Work-Life Balance：✅ 工作優先
  • 風險因素：0 個

⚠️ 保證期建議：60 天（標準）

📞 聯絡方式：
• Email: zhangdaming@email.com
• Phone: 0912-345-678
• LinkedIn: linkedin.com/in/zhangdaming

要聯繫此候選人？回覆「聯繫 張大明」」
```

---

### 場景 4：批量 AI 配對（Topic 304）

```
用戶 @ Topic 304：
「@YuQi 配對 AI工程師」

YuQi：
「🤖 開始 AI 配對...

從履歷池中找到 50 位可能候選人
正在計算配對分數...」

[30 秒後]

YuQi：
「✅ AI 配對完成！

📊 配對結果（AI工程師）：
• P0（高度匹配）：8 位 ✨
• P1（匹配）：15 位
• P2（需確認）：12 位
• REJECT（不適合）：15 位

Top 5 推薦：
1. 張大明 - 90.5 分（穩定性 A）
2. 王小明 - 88.2 分（穩定性 B）
3. 李四 - 85.7 分（穩定性 B）
4. 趙六 - 83.5 分（穩定性 A）
5. 錢七 - 82.1 分（穩定性 B）

完整配對結果已更新至履歷池
查看詳細報告？回覆「報告 AI工程師」」
```

---

### 場景 5：候選人文化適配評估（Topic 304）

```
用戶 @ Topic 304：
「@YuQi 文化評估 張大明 AI工程師」

YuQi：
「🏢 文化適配評估

👤 候選人：張大明
💼 職缺：AI工程師（快節奏AI科技公司）

📊 文化適配度：85/100（高度適配）

詳細對比：
✅ 工作節奏：快速變化 ↔ 快速迭代（100 分）
✅ 加班文化：可以接受 ↔ 經常加班（80 分）
✅ 溝通方式：直接坦率 ↔ 直接坦率（100 分）
✅ 職涯發展：快速晉升 ↔ 快速晉升（100 分）
⚠️ WLB 重視度：工作優先 ↔ 工作優先（90 分）
   （候選人 WLB 排名第 8，可能略有壓力）

🎯 風險因素：0 個
⏰ 保證期建議：60 天（標準）
📈 預估留任率：95%

結論：✅ 強烈推薦（文化高度適配）」
```

---

### 場景 6：產生配對報告（Topic 326）

```
用戶 @ Topic 326：
「@YuQi 報告 AI工程師」

YuQi：
「📊 AI工程師 - 配對報告

🔍 搜尋來源：
• GitHub：15 位
• LinkedIn：20 位
• 履歷池：15 位
• 總計：50 位

📈 配對分佈：
• P0（80+ 分）：8 位（16%）
• P1（60-80 分）：15 位（30%）
• P2（40-60 分）：12 位（24%）
• REJECT（<40 分）：15 位（30%）

🎯 Top 5 推薦：

1. 張大明 - 90.5 分
   • 技能：28/30
   • 經驗：18/20
   • 穩定性：27/30（A 級，極低風險）
   • 文化：85/100（高度適配）
   • 保證期：60 天
   
2. 王小明 - 88.2 分
   • 技能：27/30
   • 經驗：20/20
   • 穩定性：25/30（B 級，低風險）
   • 文化：80/100（適配）
   • 保證期：60 天
   
...

完整 PDF 報告已產生：
https://drive.google.com/xxx

要安排面試？回覆「面試 張大明」」
```

---

## 🤖 指令設計

### Topic 319（JD管理）

| 指令 | 功能 | 範例 |
|------|------|------|
| `@YuQi 新職缺 [職位]` | 開啟新職缺流程 | `@YuQi 新職缺 AI工程師` |
| `@YuQi JD解析` | 解析 JD 文字 | （貼上 JD 後） |
| `@YuQi 公司文化` | 取得文化問卷連結 | - |

### Topic 304（履歷池 + AI 配對）

| 指令 | 功能 | 範例 |
|------|------|------|
| `@YuQi 搜尋 [職位]` | 搜尋候選人 | `@YuQi 搜尋 AI工程師` |
| `@YuQi 配對 [職位]` | AI 配對現有候選人 | `@YuQi 配對 AI工程師` |
| `@YuQi 候選人詳情 [姓名]` | 查看候選人詳情 | `@YuQi 候選人詳情 張大明` |
| `@YuQi 文化評估 [姓名] [職位]` | 文化適配評估 | `@YuQi 文化評估 張大明 AI工程師` |
| `@YuQi 穩定性 [姓名]` | 查看穩定性評分 | `@YuQi 穩定性 張大明` |

### Topic 326（報告 + 總覽）

| 指令 | 功能 | 範例 |
|------|------|------|
| `@YuQi 報告 [職位]` | 產生配對報告 | `@YuQi 報告 AI工程師` |
| `@YuQi 總覽` | Pipeline 總覽 | - |

---

## 🔧 技術實作方案

### 方案 A：擴展現有腳本（推薦）

在現有的 Telegram bot handler 中新增功能：

```bash
# 檔案位置
/Users/user/clawd/hr-tools/telegram-bot-handler.sh

# 新增處理邏輯
if [[ "$message" =~ "@YuQi 配對" ]]; then
    job_title=$(echo "$message" | sed 's/@YuQi 配對 //')
    python3 /Users/user/clawd/hr-tools/ai-matching-pipeline.sh "$job_title" "$chat_id" "$topic_id"
fi
```

### 方案 B：建立獨立 Python Bot

```python
# /Users/user/clawd/hr-tools/telegram-ai-bot.py

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

async def handle_ai_matching(update: Update, context):
    """處理 AI 配對請求"""
    chat_id = update.effective_chat.id
    message_thread_id = update.effective_message.message_thread_id
    
    # 只在 Topic 304 處理
    if message_thread_id != 304:
        return
    
    # 執行 AI 配對
    job_title = context.args[0] if context.args else None
    # ... 呼叫 ai_matcher_v2.py
    
async def handle_stability_check(update: Update, context):
    """處理穩定性評分請求"""
    # ... 呼叫 stability_predictor_v2.py
```

### 方案 C：整合到現有 Cron（自動化）

```bash
# 每天 09:00 自動執行
# Cron: 0 9 * * * /Users/user/clawd/hr-tools/auto-ai-matching.sh

#!/bin/bash
# auto-ai-matching.sh

# 1. 讀取所有「招募中」職缺
jobs=$(python3 jd-manager.sh list --status 招募中)

# 2. 逐個職缺執行 AI 配對
for job in $jobs; do
    python3 ai-matching-pipeline.py --job "$job" --notify-topic 304
done
```

---

## 📝 實作步驟

### Phase 1：基礎整合（1-2 天）

1. **建立 AI 配對整合腳本**
   ```bash
   /Users/user/clawd/hr-tools/ai-matching-pipeline.sh
   ```
   - 輸入：職位名稱
   - 輸出：Telegram 訊息（Topic 304）

2. **測試指令**
   - 在 Topic 304 測試 `@YuQi 配對 AI工程師`
   - 確認回覆格式正確

3. **建立報告產生腳本**
   ```bash
   /Users/user/clawd/hr-tools/generate-matching-report.py
   ```

### Phase 2：問卷整合（2-3 天）

1. **建立 Google Forms 問卷**
   - 公司文化問卷
   - 候選人價值觀問卷

2. **設定問卷回覆通知**
   - Google Forms → Telegram 通知
   - 自動觸發 AI 配對

3. **測試完整流程**
   - 新職缺 → 填問卷 → 搜尋 → 配對 → 報告

### Phase 3：自動化優化（1 週）

1. **每日自動配對**
   - Cron 自動執行
   - 新候選人自動評分

2. **智能推薦**
   - 職缺更新時自動重新配對
   - Top 5 候選人變化提醒

---

## 🎯 建議優先順序

### 立刻可做（今天）
1. ✅ 在 Topic 304 手動測試 AI 配對
   ```
   你：@YuQi 我要測試 AI 配對
   我：（執行腳本，回傳結果）
   ```

2. ✅ 產生第一份配對報告
   ```bash
   cd /Users/user/clawd/hr-tools
   python3 generate-matching-report.py --job "AI工程師"
   ```

### 本週內（2-3 天）
3. 建立 Telegram 指令 handler
4. 建立 Google Forms 問卷
5. 整合問卷 → AI 配對流程

### 下週（1 週）
6. 設定自動化 Cron
7. 優化訊息格式
8. 建立完整使用手冊

---

**你想從哪個開始？** 🚀
- A）立刻在 Topic 304 手動測試
- B）先建立 Google Forms 問卷
- C）建立完整 Telegram bot
- D）其他想法
