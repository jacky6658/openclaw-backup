#!/bin/bash
# 自動履歷歸檔系統
# 每小時檢查 Topic 4（履歷進件），自動解析 + 匯入履歷池

set -euo pipefail

RESUME_DIR="/Users/user/clawd/hr-recruitment/inbox"
POOL_SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT="aiagentg888@gmail.com"
PROCESSED_LOG="/Users/user/clawd/hr-tools/data/processed-resumes.log"

mkdir -p "$(dirname "$PROCESSED_LOG")"
touch "$PROCESSED_LOG"

echo "📂 檢查新履歷..."

# 檢查 inbox 目錄是否有新 PDF
new_count=$(find "$RESUME_DIR" -name "*.pdf" -type f 2>/dev/null | wc -l | tr -d ' ')

if [ "$new_count" -eq 0 ]; then
    echo "✓ 無新履歷"
    exit 0
fi

echo "📄 發現 $new_count 個新履歷，開始處理..."

# 使用 Python 批次解析
python3 << 'PYTHON_EOF'
import os
import json
from pathlib import Path
import pdfplumber

RESUME_DIR = Path("/Users/user/clawd/hr-recruitment/inbox")
PROCESSED_LOG = "/Users/user/clawd/hr-tools/data/processed-resumes.log"
OUTPUT_JSON = "/tmp/auto-parsed-resumes.json"

# 讀取已處理清單
processed = set()
if os.path.exists(PROCESSED_LOG):
    with open(PROCESSED_LOG, 'r') as f:
        processed = set(line.strip() for line in f)

# 找出未處理的 PDF
pdf_files = list(RESUME_DIR.glob('*.pdf'))
new_files = [f for f in pdf_files if f.name not in processed]

if not new_files:
    print("✓ 所有履歷已處理")
    exit(0)

print(f"🔄 處理 {len(new_files)} 個新履歷...")

results = []
for pdf_path in new_files:
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            text = ''
            for page in pdf.pages[:2]:
                text += page.extract_text() or ''
        
        # 簡單提取姓名（第一行）
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        name = lines[0][:50] if lines else "未知"
        
        # 簡單技能匹配
        text_lower = text.lower()
        skills = []
        for kw in ['sap', 'excel', 'erp', 'accounting', 'finance', 'taxation']:
            if kw in text_lower:
                skills.append(kw.upper())
        
        results.append([
            name, "待補充", "Finance Manager", 
            ', '.join(skills[:3]) if skills else "待確認",
            "待確認", "待確認", pdf_path.name,
            "新進履歷", "Jacky", "自動歸檔",
            "2026-02-12", "2026-02-12"
        ])
        
        # 記錄已處理
        with open(PROCESSED_LOG, 'a') as f:
            f.write(f"{pdf_path.name}\n")
        
        print(f"✓ {name}")
    except Exception as e:
        print(f"✗ {pdf_path.name}: {e}")

# 輸出 JSON
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False)

print(f"\n✅ 解析完成：{len(results)} 人")
PYTHON_EOF

# 匯入 Google Sheets
if [ -f /tmp/auto-parsed-resumes.json ]; then
    count=$(jq 'length' /tmp/auto-parsed-resumes.json)
    
    if [ "$count" -gt 0 ]; then
        echo "📊 匯入 $count 筆到履歷池..."
        gog sheets append "$POOL_SHEET_ID" "工作表1!A:L" \
            --values-json "$(cat /tmp/auto-parsed-resumes.json)" \
            --insert INSERT_ROWS \
            --account "$ACCOUNT"
        
        echo "✅ 自動歸檔完成！"
    fi
fi
