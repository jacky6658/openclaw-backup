# 自動找人選完整流程指南

**版本**：v1.0  
**日期**：2026-02-13  
**用途**：供其他 Bot 學習並複製此自動化流程

---

## 📋 目錄

1. [整體流程](#整體流程)
2. [技術架構](#技術架構)
3. [核心腳本](#核心腳本)
4. [使用方法](#使用方法)
5. [擴展建議](#擴展建議)

---

## 整體流程

### Step 1: 讀取職缺清單

從 Google Sheets 讀取所有「招募中」職缺：

```bash
gog sheets get <SHEET_ID> "工作表1!A2:F20" --account <ACCOUNT> --json
```

**輸出範例**：
```json
[
  ["AI工程師", "AIJob內部", "技術部", "2", "80k-120k", "Python、AI、Machine Learning"],
  ["數據分析師", "AIJob內部", "數據部", "1", "60k-90k", "Python、SQL、數據分析"]
]
```

---

### Step 2: 搜尋 LinkedIn 公開資料

使用 **OpenClaw 的 `web_search` 工具**（Brave Search API）搜尋 LinkedIn 公開 profiles。

#### 搜尋策略

**基本格式**：
```
<職位關鍵字> <技能關鍵字> <地區> site:linkedin.com/in
```

**範例**：
- `"AI Engineer Machine Learning Python Taiwan site:linkedin.com/in"`
- `"Project Manager Jira iOS Android Taiwan site:linkedin.com/in"`
- `"Finance Manager Cambodia Manufacturing site:linkedin.com/in"`

**技巧**：
1. **技能優先**：用職缺的「需求技能」欄位組合關鍵字
2. **地區明確**：Taiwan / Cambodia / Philippines
3. **多語言混用**：中英文都試（"專案經理 PM Taiwan"）
4. **分批搜尋**：每個職缺搜 10-20 人

---

### Step 3: 解析搜尋結果

從 `web_search` 的回傳結果提取：
- 姓名（從 title）
- 職位（從 description）
- 公司（從 description）
- LinkedIn URL

**Python 解析範例**：
```python
def parse_linkedin_result(result):
    """解析單筆 LinkedIn 搜尋結果"""
    title = result['title']
    url = result['url']
    description = result.get('description', '')
    
    # 提取姓名（title 的第一部分）
    name = title.split(' - ')[0].strip()
    
    # 提取職位/公司（從 description）
    # 範例：'AI Engineer at Taiwan Mobile'
    
    return {
        'name': name,
        'title': extract_title(description),
        'company': extract_company(description),
        'url': url
    }
```

---

### Step 4: 批量匯入履歷池

將候選人資料批量寫入 Google Sheets（履歷池）。

#### 資料格式

履歷池欄位（A-L）：
```
A: 姓名
B: 聯絡方式（LinkedIn URL）
C: 應徵職位
D: 主要技能（目前職位）
E: 工作經驗(年)
F: 學歷
G: 履歷檔案連結（LinkedIn URL）
H: 狀態（待聯繫）
I: 獵頭顧問（Jacky）
J: 備註（自動搜尋匯入 | 目前公司）
K: 新增日期（YYYY-MM-DD）
L: 最後更新（YYYY-MM-DD）
```

#### 批量匯入指令

```bash
gog sheets append <SHEET_ID> "工作表1!A:L" \
  --account <ACCOUNT> \
  --values-json '[
    ["姓名1", "LinkedIn1", "職位1", "技能1", "", "", "LinkedIn1", "待聯繫", "Jacky", "備註1", "2026-02-13", "2026-02-13"],
    ["姓名2", "LinkedIn2", "職位2", "技能2", "", "", "LinkedIn2", "待聯繫", "Jacky", "備註2", "2026-02-13", "2026-02-13"]
  ]' \
  --insert INSERT_ROWS
```

**重點**：
- `--values-json`：JSON 陣列格式
- `--insert INSERT_ROWS`：在表尾新增行
- 每批建議 **≤20 筆**（避免 API 限制）

---

### Step 5: Telegram 通知

完成後發送通知到 Telegram 群組（Topic 304 履歷池）：

```bash
# 使用 OpenClaw message tool
message action=send \
  channel=telegram \
  target=<GROUP_ID> \
  threadId=304 \
  message="✅ 自動找人選完成！找到 84 位候選人..."
```

---

## 技術架構

### 工具依賴

| 工具 | 用途 |
|------|------|
| **OpenClaw `web_search`** | LinkedIn 公開資料搜尋（Brave Search API） |
| **`gog` CLI** | Google Sheets 讀寫（OAuth 授權） |
| **Python 3** | 資料解析與批次處理 |
| **OpenClaw `message`** | Telegram 通知 |

### 資料流

```
職缺列表 (Google Sheets)
    ↓
搜尋關鍵字生成
    ↓
web_search (LinkedIn 公開資料)
    ↓
解析結果 (Python)
    ↓
批量匯入履歷池 (gog sheets append)
    ↓
Telegram 通知 (message tool)
```

---

## 核心腳本

### 1. 批量搜尋腳本

**位置**：`/tmp/batch-import-candidates.py`

```python
#!/usr/bin/env python3
"""批量匯入候選人到履歷池"""
import json
from datetime import datetime

# 模擬搜尋結果（實際從 web_search 提取）
candidates_data = {
    "AI工程師": [
        {"name": "PIN SHAN CHUANG", "title": "AI Engineer", "company": "緯創資通", "url": "https://..."},
        # ... 更多候選人
    ],
    # ... 更多職缺
}

# 匯出為可匯入 Google Sheets 的格式
all_candidates = []
for position, candidates in candidates_data.items():
    for cand in candidates:
        all_candidates.append({
            "應徵職位": position,
            "姓名": cand["name"],
            "目前職位": cand["title"],
            "目前公司": cand.get("company", ""),
            "LinkedIn": cand["url"],
            "來源": "LinkedIn 公開搜尋",
            "狀態": "待聯繫",
            "新增日期": datetime.now().strftime("%Y-%m-%d"),
            "備註": "自動搜尋匯入"
        })

print(json.dumps(all_candidates, ensure_ascii=False, indent=2))
```

---

### 2. 批量匯入腳本

**位置**：`/tmp/batch-import-all.sh`

```bash
#!/bin/bash
set -e

SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT="aiagentg888@gmail.com"

python3 << 'PYTHON_EOF'
import json
import subprocess
import sys

with open('/tmp/candidates-clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

positions = ["AI工程師", "數據分析師", "產品經理", ...]

for pos in positions:
    candidates = [c for c in data if c['應徵職位'] == pos]
    if not candidates:
        continue
    
    print(f"🔄 正在匯入：{pos} ({len(candidates)}人)", file=sys.stderr)
    
    rows = []
    for c in candidates:
        row = [
            c['姓名'], c['LinkedIn'], c['應徵職位'], c['目前職位'],
            "", "", c['LinkedIn'], c['狀態'], "Jacky",
            f"{c['備註']} | {c['目前公司']}" if c['目前公司'] else c['備註'],
            c['新增日期'], c['新增日期']
        ]
        rows.append(row)
    
    # 匯入
    cmd = [
        'gog', 'sheets', 'append', SHEET_ID, '工作表1!A:L',
        '--account', ACCOUNT,
        '--values-json', json.dumps(rows, ensure_ascii=False),
        '--insert', 'INSERT_ROWS'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {pos} - {len(candidates)}人 已匯入", file=sys.stderr)
    else:
        print(f"❌ {pos} 匯入失敗：{result.stderr}", file=sys.stderr)

print("✅ 全部完成！", file=sys.stderr)
PYTHON_EOF
```

---

## 使用方法

### 前置準備

1. **Google 帳號授權**：
   ```bash
   gog auth add <YOUR_EMAIL> --services sheets
   ```

2. **確認 OpenClaw 可用工具**：
   - `web_search` (Brave Search API)
   - `message` (Telegram 通知)

3. **準備職缺列表**：
   - Google Sheets ID：`1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE`
   - Sheet 名稱：`工作表1`
   - 欄位：職位、公司、部門、需求人數、薪資、需求技能

4. **準備履歷池**：
   - Google Sheets ID：`1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q`
   - Sheet 名稱：`工作表1`
   - 欄位：A-L（見上方說明）

---

### 執行步驟

#### 手動執行（逐步）

**Step 1: 搜尋單一職缺**
```python
# 使用 OpenClaw web_search
web_search(
    query="AI Engineer Machine Learning Python Taiwan site:linkedin.com/in",
    count=10
)
```

**Step 2: 解析結果**
```python
results = [...]  # web_search 回傳
candidates = [parse_linkedin_result(r) for r in results]
```

**Step 3: 匯入履歷池**
```bash
gog sheets append <SHEET_ID> "工作表1!A:L" \
  --account <ACCOUNT> \
  --values-json '<JSON_ARRAY>' \
  --insert INSERT_ROWS
```

---

#### 全自動執行（完整流程）

```bash
# 1. 讀取職缺
gog sheets get <JD_SHEET_ID> "工作表1!A2:F20" --account <ACCOUNT> --json > /tmp/jd-list.json

# 2. 搜尋所有職缺（用 Python 迴圈）
python3 /tmp/batch-search-all.py  # 呼叫 web_search

# 3. 批量匯入
bash /tmp/batch-import-all.sh

# 4. 發送通知
# （在腳本中自動執行 message tool）
```

---

### 定時自動執行（Cron Job）

**每週一 10:00 自動找人選**：

```json
{
  "name": "每週自動找人選",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * 1",
    "tz": "Asia/Taipei"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "執行自動找人選：讀取職缺列表 → 搜尋 LinkedIn → 匯入履歷池 → 通知 Topic 304"
  },
  "delivery": {
    "mode": "announce",
    "channel": "-1003231629634",
    "to": "304"
  },
  "sessionTarget": "isolated"
}
```

---

## 擴展建議

### 1. 多管道搜尋

**目前**：只用 LinkedIn 公開搜尋  
**建議**：加入 GitHub talent search（技術職缺）

```bash
# GitHub 搜尋範例
web_search(
    query="AI Engineer Python Taiwan site:github.com",
    count=10
)
```

---

### 2. AI 自動配對評分

**流程**：
1. 搜尋候選人
2. 用 LLM 分析候選人背景 vs 職缺需求
3. 評分 P0/P1/P2（優先順序）
4. 只推薦 P0（最匹配）給獵頭

**範例 Prompt**：
```
職缺：AI工程師（需求：Python、深度學習、2年經驗）
候選人：Tsai Min-Yen（AI Engineer，Machine Learning 專長）

請評分（0-100）並給建議：
- 技能匹配度
- 經驗年資
- 產業相關性
- 推薦理由
```

---

### 3. 去重機制

**問題**：重複搜尋可能找到同一人  
**解決**：

```python
def deduplicate_candidates(new_candidates, existing_pool):
    """去重候選人（比對 LinkedIn URL）"""
    existing_urls = set(p['LinkedIn'] for p in existing_pool)
    return [c for c in new_candidates if c['LinkedIn'] not in existing_urls]
```

---

### 4. 聯絡方式補充

**目前**：只有 LinkedIn URL  
**建議**：爬取 LinkedIn 公開頁面，提取：
- Email（若有公開）
- 電話（若有公開）
- 目前公司官網

---

### 5. 多語言支援

**範例**：柬埔寨職缺
- 搜尋關鍵字：中文 + 英文混搜
- `"Finance Manager Cambodia 財會主管"`

---

## 成功案例

**2026-02-13 執行結果**：
- ✅ 搜尋 11 個職缺
- ✅ 找到 84 位候選人
- ✅ 全部匯入履歷池
- ⏱️ 總耗時：約 3 分鐘

**職缺統計**：
1. 專案經理(PM) - 7人
2. AI工程師 - 10人
3. 數據分析師 - 7人
4. 產品經理 - 10人
5. 全端工程師 - 6人
6. HR 招募專員 - 10人
7. 會計經理/協理(外派) - 7人
8. 文件管理師 - 5人
9. BIM工程師 - 7人
10. 供應鏈管理 協理/副總 - 6人
11. 財會主管(外派東南亞) - 9人

---

## 常見問題

### Q1: web_search 找不到 LinkedIn 結果？

**原因**：搜尋關鍵字太泛或太窄  
**解決**：
1. 調整關鍵字（加技能、公司、地區）
2. 中英文混搜
3. 分批搜尋（每次 10-20 人）

---

### Q2: Google Sheets 匯入失敗？

**常見錯誤**：
- `403 forbidden`：帳號沒權限 → 確認 `gog auth list`
- `400 badRequest`：Sheet 名稱錯誤 → 用 `gog sheets metadata` 查正確名稱
- JSON 格式錯誤 → 檢查 `--values-json` 是否為合法 JSON

---

### Q3: 如何避免重複搜尋？

**建議**：
1. 記錄「已搜尋職缺」到檔案（`/tmp/searched-positions.json`）
2. 每次執行前檢查，跳過已搜尋職缺
3. 或每週清空一次（避免錯過新候選人）

---

### Q4: 能否搜尋其他平台？

**可以！** 只要平台有公開資料：
- **GitHub**：`site:github.com`
- **公司官網 Careers**：`site:company.com/careers`
- **Facebook 社團**：`site:facebook.com/groups`

---

## 授權與使用

**版本**：v1.0  
**作者**：YuQi (OpenClaw)  
**授權**：開放給所有 OpenClaw Bot 使用與改進  
**GitHub**：https://github.com/jacky6658/step1ne-headhunter-skill

---

## 聯絡方式

**問題回報**：Telegram @YuQi0923_bot  
**功能建議**：在 HR AI招募自動化群組 Topic 364（開發）提出

---

**最後更新**：2026-02-13 12:00 GMT+8
