# 快速開始：在 Telegram 使用 AI 招聘系統

**目標**：5 分鐘內在 Telegram 看到第一次 AI 配對結果  
**群組**：HR AI招募自動化 (`-1003231629634`)  
**Topic**：#2履歷池 (304)

---

## 🚀 方法 1：立刻測試（手動）

### 步驟 1：執行 AI 配對腳本
```bash
cd /Users/user/clawd/hr-tools
python3 ai-matching-batch.py "AI工程師"
```

**預期輸出**：
```
找到 3 位候選人

📊 配對分佈：
• P0（高度匹配）：1 位 ✨
• P1（匹配）：0 位
• P2（需確認）：1 位
• REJECT（不適合）：1 位

🎯 Top 5 推薦：

1. 張大明 - 84.0 分（P0）
   穩定性：90/100 (A（極穩定）)
   技能：Python, TensorFlow, PyTorch

2. 李小華 - 28.8 分（REJECT）
   穩定性：35/100 (D（不穩定）)
   技能：Python, SQL, Tableau

3. 王小明 - 10.7 分（REJECT）
   穩定性：10/100 (F（極不穩定）)
   技能：JavaScript, React, Node.js
```

### 步驟 2：手動複製到 Telegram

1. 打開 Telegram「HR AI招募自動化」群組
2. 進入 Topic 304（#2履歷池）
3. 貼上上面的結果
4. ✅ 完成！

---

## 🤖 方法 2：使用 message 指令（自動發送）

### 步驟 1：創建發送腳本
```bash
cd /Users/user/clawd/hr-tools
cat > send-matching-result.sh << 'EOF'
#!/bin/bash

JOB_TITLE="$1"
RESULT=$(python3 ai-matching-batch.py "$JOB_TITLE")

MESSAGE="✅ AI工程師 - 配對完成！

$RESULT

完整清單已更新至履歷池
查看詳情：https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"

echo "$MESSAGE"

# 發送到 Telegram
# message --action send --channel telegram \
#   --target "-1003231629634" \
#   --thread "304" \
#   --message "$MESSAGE"
EOF

chmod +x send-matching-result.sh
```

### 步驟 2：執行腳本
```bash
./send-matching-result.sh "AI工程師"
```

### 步驟 3：啟用自動發送

取消註解最後 3 行（移除 `#`）：
```bash
message --action send --channel telegram \
  --target "-1003231629634" \
  --thread "304" \
  --message "$MESSAGE"
```

---

## 🎯 方法 3：整合到指令系統（完整版）

### 步驟 1：創建 Telegram 指令處理器

```bash
cd /Users/user/clawd/hr-tools
cat > telegram-command-handler.sh << 'EOF'
#!/bin/bash
# Telegram 指令處理器

MESSAGE="$1"
CHAT_ID="$2"
TOPIC_ID="$3"

# 檢查是否為 Topic 304
if [ "$TOPIC_ID" != "304" ]; then
    exit 0
fi

# 處理「@YuQi 配對 [職位]」
if [[ "$MESSAGE" =~ "@YuQi 配對" ]]; then
    JOB_TITLE=$(echo "$MESSAGE" | sed 's/@YuQi 配對 //')
    
    # 發送「處理中」訊息
    message --action send --channel telegram \
      --target "$CHAT_ID" \
      --thread "$TOPIC_ID" \
      --message "🤖 開始 AI 配對：$JOB_TITLE..."
    
    # 執行配對
    RESULT=$(python3 /Users/user/clawd/hr-tools/ai-matching-batch.py "$JOB_TITLE")
    
    # 發送結果
    message --action send --channel telegram \
      --target "$CHAT_ID" \
      --thread "$TOPIC_ID" \
      --message "✅ 配對完成！

$RESULT"
fi

# 處理「@YuQi 候選人詳情 [姓名]」
if [[ "$MESSAGE" =~ "@YuQi 候選人詳情" ]]; then
    NAME=$(echo "$MESSAGE" | sed 's/@YuQi 候選人詳情 //')
    
    # 這裡應該查詢候選人詳細資料
    # 簡化版：回覆固定訊息
    message --action send --channel telegram \
      --target "$CHAT_ID" \
      --thread "$TOPIC_ID" \
      --message "👤 候選人：$NAME

功能開發中... 🚧"
fi
EOF

chmod +x telegram-command-handler.sh
```

### 步驟 2：測試指令

在 Telegram Topic 304 發送：
```
@YuQi 配對 AI工程師
```

應該會收到：
```
🤖 開始 AI 配對：AI工程師...

（30 秒後）

✅ 配對完成！
...
```

---

## 📝 可用指令清單

### Topic 304（履歷池）

| 指令 | 功能 | 狀態 |
|------|------|------|
| `@YuQi 配對 [職位]` | AI 配對現有候選人 | ✅ 可用 |
| `@YuQi 候選人詳情 [姓名]` | 查看候選人詳情 | 🚧 開發中 |
| `@YuQi 穩定性 [姓名]` | 查看穩定性評分 | 🚧 開發中 |
| `@YuQi 文化評估 [姓名] [職位]` | 文化適配評估 | 🚧 開發中 |

### Topic 319（JD列表）

| 指令 | 功能 | 狀態 |
|------|------|------|
| `@YuQi 新職缺 [職位]` | 開啟新職缺流程 | 🚧 開發中 |
| `@YuQi JD解析` | 解析 JD 文字 | 🚧 開發中 |

### Topic 326（總覽看板）

| 指令 | 功能 | 狀態 |
|------|------|------|
| `@YuQi 報告 [職位]` | 產生配對報告 | 🚧 開發中 |

---

## 🔧 進階設定

### 自動化 Cron（每天自動配對）

```bash
# 每天 09:00 自動執行
crontab -e

# 新增這一行
0 9 * * * /Users/user/clawd/hr-tools/send-matching-result.sh "AI工程師" >> /tmp/ai-matching.log 2>&1
```

### Google Sheets 整合

實際使用時應從 Google Sheets 讀取：
- JD 資料：`1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE`
- 履歷池：`1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q`

修改 `ai-matching-batch.py`：
```python
# 從 Google Sheets 讀取 JD
import subprocess
jd_data = subprocess.run(
    ['gog', 'sheets', 'get', '1QPae...', '--range', 'A2:Z100'],
    capture_output=True, text=True
).stdout
```

---

## ✅ 驗證清單

- [ ] 執行 `ai-matching-batch.py` 成功
- [ ] 在 Telegram 看到配對結果
- [ ] （選做）啟用自動發送
- [ ] （選做）設定 Cron 自動化
- [ ] （選做）整合 Google Sheets

---

## 🎯 下一步

1. **今天**：手動測試 AI 配對
2. **明天**：建立 Google Forms 問卷
3. **本週**：整合 Telegram 指令系統
4. **下週**：自動化 + 完整報告

---

**準備好測試了嗎？** 🚀

立刻執行：
```bash
cd /Users/user/clawd/hr-tools
python3 ai-matching-batch.py "AI工程師"
```
