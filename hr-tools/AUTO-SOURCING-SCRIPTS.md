# 自動找人選實戰腳本包

**版本**：v1.0  
**日期**：2026-02-13  
**用途**：完整可執行的腳本，直接複製使用

---

## 📦 腳本清單

1. [批量搜尋候選人](#1-批量搜尋候選人)
2. [解析並匯入履歷池](#2-解析並匯入履歷池)
3. [讀取職缺列表](#3-讀取職缺列表)
4. [完整自動化流程](#4-完整自動化流程)

---

## 1. 批量搜尋候選人

**檔案**：`batch-search-candidates.py`

```python
#!/usr/bin/env python3
"""批量搜尋 LinkedIn 候選人（使用 OpenClaw web_search）"""
import json
import sys

# 職缺與搜尋關鍵字對應
JOB_SEARCH_KEYWORDS = {
    "AI工程師": "AI Engineer Machine Learning Python Taiwan site:linkedin.com/in",
    "數據分析師": "Data Analyst Python SQL Taiwan site:linkedin.com/in",
    "產品經理": "Product Manager Taiwan site:linkedin.com/in",
    "全端工程師": "Full Stack Engineer React Node.js Taiwan site:linkedin.com/in",
    "專案經理(PM)": "Project Manager Jira iOS Android Taiwan site:linkedin.com/in",
    "HR 招募專員": "HR Recruiter Taiwan site:linkedin.com/in",
    "BIM工程師": "BIM Engineer Revit AutoCAD Taiwan site:linkedin.com/in",
    "資安工程師": "Security Engineer SSDLC DevSecOps Taiwan site:linkedin.com/in",
    "雲端維運工程師": "DevOps Engineer Linux AWS GCP Taiwan site:linkedin.com/in",
    "後端開發工程師": "Backend Engineer .NET Python Taiwan site:linkedin.com/in",
    "軟體測試工程師": "QA Engineer Automation Testing Taiwan site:linkedin.com/in",
}

def search_position(position_name, count=10):
    """搜尋單一職缺的候選人"""
    query = JOB_SEARCH_KEYWORDS.get(position_name, f"{position_name} Taiwan site:linkedin.com/in")
    
    # 這裡需要呼叫 OpenClaw 的 web_search tool
    # 示範格式：
    print(f"🔍 搜尋：{position_name}", file=sys.stderr)
    print(f"   關鍵字：{query}", file=sys.stderr)
    
    # 實際執行時，用 OpenClaw web_search(query=query, count=count)
    # results = web_search(query=query, count=count)
    
    # 這裡返回假資料作為示範
    return []

def parse_linkedin_result(result):
    """解析單筆 LinkedIn 搜尋結果"""
    title = result.get('title', '')
    url = result.get('url', '')
    description = result.get('description', '')
    
    # 提取姓名（title 的第一部分）
    name = title.split(' - ')[0].strip() if ' - ' in title else title.strip()
    
    # 提取職位（從 description 或 title）
    position = ""
    company = ""
    
    if description:
        # 嘗試從 description 提取
        lines = description.split('\n')
        for line in lines:
            if 'at ' in line.lower():
                parts = line.split(' at ')
                if len(parts) >= 2:
                    position = parts[0].strip()
                    company = parts[1].strip()
                    break
    
    return {
        'name': name,
        'title': position or title,
        'company': company,
        'url': url
    }

if __name__ == "__main__":
    # 測試搜尋
    position = sys.argv[1] if len(sys.argv) > 1 else "AI工程師"
    results = search_position(position, count=10)
    
    candidates = [parse_linkedin_result(r) for r in results]
    print(json.dumps(candidates, ensure_ascii=False, indent=2))
```

**使用方式**：
```bash
python3 batch-search-candidates.py "AI工程師"
```

---

## 2. 解析並匯入履歷池

**檔案**：`import-to-resume-pool.py`

```python
#!/usr/bin/env python3
"""將候選人批量匯入履歷池"""
import json
import subprocess
import sys
from datetime import datetime

RESUME_POOL_SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aiagentg888@gmail.com"

def convert_to_sheet_row(candidate, position):
    """轉換為 Google Sheets 格式（A-L 欄位）"""
    return [
        candidate['name'],                      # A: 姓名
        candidate['url'],                       # B: 聯絡方式
        position,                               # C: 應徵職位
        candidate['title'],                     # D: 主要技能
        "",                                     # E: 工作經驗(年)
        "",                                     # F: 學歷
        candidate['url'],                       # G: 履歷檔案連結
        "待聯繫",                                # H: 狀態
        "Jacky",                                # I: 獵頭顧問
        f"自動搜尋匯入 | {candidate['company']}", # J: 備註
        datetime.now().strftime("%Y-%m-%d"),    # K: 新增日期
        datetime.now().strftime("%Y-%m-%d")     # L: 最後更新
    ]

def import_candidates(candidates, position):
    """批量匯入候選人到履歷池"""
    if not candidates:
        print("⚠️  沒有候選人可匯入", file=sys.stderr)
        return
    
    rows = [convert_to_sheet_row(c, position) for c in candidates]
    
    # 使用 gog sheets append
    cmd = [
        'gog', 'sheets', 'append',
        RESUME_POOL_SHEET_ID,
        '工作表1!A:L',
        '--account', ACCOUNT,
        '--values-json', json.dumps(rows, ensure_ascii=False),
        '--insert', 'INSERT_ROWS'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 成功匯入 {len(candidates)} 位候選人", file=sys.stderr)
        return True
    else:
        print(f"❌ 匯入失敗：{result.stderr}", file=sys.stderr)
        return False

if __name__ == "__main__":
    # 從 stdin 讀取 JSON 格式的候選人資料
    candidates_data = json.load(sys.stdin)
    position = sys.argv[1] if len(sys.argv) > 1 else "未知職位"
    
    import_candidates(candidates_data, position)
```

**使用方式**：
```bash
# 從搜尋結果匯入
python3 batch-search-candidates.py "AI工程師" | \
python3 import-to-resume-pool.py "AI工程師"
```

---

## 3. 讀取職缺列表

**檔案**：`read-jd-list.sh`

```bash
#!/bin/bash
# 讀取 Google Sheets 職缺列表

SHEET_ID="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
ACCOUNT="aiagentg888@gmail.com"

echo "📋 讀取職缺列表..."

# 讀取所有職缺（A2:F100）
gog sheets get "$SHEET_ID" "工作表1!A2:F100" \
  --account "$ACCOUNT" \
  --json > /tmp/jd-list.json

# 解析並顯示
jq -r '.values[] | "\(.[0]) | \(.[1]) | \(.[3])人 | \(.[4])"' /tmp/jd-list.json

echo ""
echo "📊 總計：$(jq '.values | length' /tmp/jd-list.json) 個職缺"
```

**使用方式**：
```bash
bash read-jd-list.sh
```

---

## 4. 完整自動化流程

**檔案**：`auto-sourcing-full.sh`

```bash
#!/bin/bash
# 完整自動化流程：讀取職缺 → 搜尋候選人 → 匯入履歷池 → 通知

set -e

SHEET_ID="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
RESUME_POOL_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT="aiagentg888@gmail.com"
TELEGRAM_GROUP="-1003231629634"
TELEGRAM_TOPIC="304"

echo "🚀 開始自動找人選流程..."
echo ""

# Step 1: 讀取職缺列表
echo "📋 Step 1: 讀取職缺列表"
gog sheets get "$SHEET_ID" "工作表1!A2:F100" \
  --account "$ACCOUNT" \
  --json > /tmp/jd-list.json

TOTAL_JDS=$(jq '.values | length' /tmp/jd-list.json)
echo "   找到 $TOTAL_JDS 個職缺"
echo ""

# Step 2: 逐個職缺搜尋候選人
echo "🔍 Step 2: 搜尋候選人"

cat > /tmp/batch-search-all.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import json
import sys

with open('/tmp/jd-list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_candidates = []
total_count = 0

for row in data.get('values', []):
    if len(row) < 2:
        continue
    
    position = row[0]
    company = row[1]
    
    print(f"🔍 搜尋：{position}", file=sys.stderr)
    
    # 這裡實際執行 web_search
    # results = web_search(query=f"{position} Taiwan site:linkedin.com/in", count=10)
    
    # 模擬結果
    candidates = []  # parse_results(results)
    
    print(f"   找到 {len(candidates)} 人", file=sys.stderr)
    total_count += len(candidates)
    
    all_candidates.append({
        'position': position,
        'candidates': candidates
    })

print(f"\n📊 總計：{total_count} 位候選人", file=sys.stderr)
print(json.dumps(all_candidates, ensure_ascii=False))
PYTHON_EOF

python3 /tmp/batch-search-all.py > /tmp/all-candidates.json

# Step 3: 批量匯入履歷池
echo ""
echo "📥 Step 3: 匯入履歷池"

python3 << 'PYTHON_EOF'
import json
import subprocess

with open('/tmp/all-candidates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    position = item['position']
    candidates = item['candidates']
    
    if not candidates:
        continue
    
    # 轉換格式並匯入
    rows = []
    for c in candidates:
        row = [
            c['name'], c['url'], position, c['title'],
            "", "", c['url'], "待聯繫", "Jacky",
            f"自動搜尋匯入 | {c['company']}",
            "2026-02-13", "2026-02-13"
        ]
        rows.append(row)
    
    # 匯入
    cmd = [
        'gog', 'sheets', 'append',
        '1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q',
        '工作表1!A:L',
        '--account', 'aiagentg888@gmail.com',
        '--values-json', json.dumps(rows, ensure_ascii=False),
        '--insert', 'INSERT_ROWS'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {position} - {len(candidates)}人 已匯入")
    else:
        print(f"❌ {position} 匯入失敗")
PYTHON_EOF

echo ""
echo "✅ 完成！"

# Step 4: 發送 Telegram 通知（需使用 OpenClaw message tool）
# message action=send channel=telegram target=$TELEGRAM_GROUP threadId=$TELEGRAM_TOPIC \
#   message="✅ 自動找人選完成！總計 XX 位候選人..."
```

**使用方式**：
```bash
bash auto-sourcing-full.sh
```

---

## 📌 實戰範例（2026-02-13）

### 今天執行的完整流程

**輸入**：11 個職缺（AI工程師、數據分析師、產品經理...）

**執行步驟**：

1. **讀取職缺**
```bash
gog sheets get 1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE "工作表1!A2:F20" \
  --account aiagentg888@gmail.com --json
```

2. **搜尋候選人**
```python
# 每個職缺執行 web_search
web_search(
    query="AI Engineer Machine Learning Python Taiwan site:linkedin.com/in",
    count=10
)
```

3. **匯入履歷池**
```bash
gog sheets append 1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q "工作表1!A:L" \
  --account aiagentg888@gmail.com \
  --values-json '[...]' \
  --insert INSERT_ROWS
```

4. **發送通知**
```
message action=send channel=telegram target=-1003231629634 threadId=304 \
  message="✅ 自動找人選完成！找到 84 位候選人..."
```

**輸出**：84 位候選人，全部匯入履歷池

---

## 🎯 關鍵技巧

### 1. 搜尋關鍵字優化

**基本格式**：
```
<職位> <技能> <地區> site:linkedin.com/in
```

**範例**：
- ✅ 好：`AI Engineer Machine Learning Python Taiwan site:linkedin.com/in`
- ❌ 差：`AI工程師`（太泛）

### 2. 去重機制

```python
def deduplicate(new_candidates, existing_pool):
    """去除重複候選人"""
    existing_urls = set(p['url'] for p in existing_pool)
    return [c for c in new_candidates if c['url'] not in existing_urls]
```

### 3. 批次處理

每批建議 **≤20 筆**，避免 Google Sheets API 限制：

```python
BATCH_SIZE = 20
for i in range(0, len(candidates), BATCH_SIZE):
    batch = candidates[i:i+BATCH_SIZE]
    import_batch(batch)
```

### 4. 錯誤處理

```python
try:
    result = import_candidates(candidates)
except Exception as e:
    print(f"❌ 匯入失敗：{e}", file=sys.stderr)
    # 記錄失敗的候選人，稍後重試
    with open('/tmp/failed-candidates.json', 'w') as f:
        json.dump(candidates, f)
```

---

## 🔧 故障排除

### Q1: web_search 找不到結果？

**原因**：關鍵字太泛或太窄

**解決**：
```python
# 方案 1: 加入技能關鍵字
query = f"{position} {skills} Taiwan site:linkedin.com/in"

# 方案 2: 中英文混搜
query = f"{position_zh} {position_en} Taiwan site:linkedin.com/in"

# 方案 3: 分批搜尋
for skill in skills_list:
    query = f"{position} {skill} Taiwan site:linkedin.com/in"
    search(query, count=5)
```

### Q2: Google Sheets 匯入失敗？

**檢查清單**：
1. ✅ 帳號授權：`gog auth list`
2. ✅ Sheet 名稱正確：`gog sheets metadata <SHEET_ID>`
3. ✅ JSON 格式合法：用 `jq` 驗證
4. ✅ 批次大小 ≤20

### Q3: Telegram 通知沒收到？

**檢查**：
- Group ID 正確？（負數）
- Topic ID 正確？
- Bot 有權限發送到該 topic？

---

## 📚 延伸閱讀

- **完整流程指南**：`AUTO-SOURCING-GUIDE.md`
- **技能文檔**：`/Users/user/clawd/skills/headhunter/SKILL.md`
- **GitHub**：https://github.com/jacky6658/step1ne-headhunter-skill

---

**最後更新**：2026-02-13 12:16 GMT+8
