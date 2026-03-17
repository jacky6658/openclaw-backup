#!/usr/bin/env python3
"""
LinkedIn PDF 完整處理流程（AI 解析版）：
1. 改檔名為人選名稱
2. 上傳 Google Drive (aiagentg888)
3. 用 Claude AI 解析 PDF → 完整結構化資料
4. 匯入 Step1ne（workHistory + educationDetails + skills + currentPosition + 穩定度）
5. 刪除本地檔案
"""

import json
import subprocess
import re
import requests
import time
import os
import sys

API_BASE = "https://api-hr.step1ne.com"
DRIVE_FOLDER_ID = "1nLVrxKDai3mxdNpNkyjk2tPwRoiyC8eM"
DRIVE_ACCOUNT = "aiagentg888@gmail.com"
OPENCLAW_TOKEN = "9b3cb3f2d661fe14d0d267a2380c3da397b4b6673539bcd7"
OPENCLAW_API = "http://localhost:18789/v1/chat/completions"


def parse_pdf(pdf_path):
    r = subprocess.run(['pdftotext', pdf_path, '-'], capture_output=True, text=True)
    return r.stdout


def ai_extract_info(text, name):
    """使用 Claude AI 解析履歷文字，回傳結構化 JSON"""
    
    prompt = f"""你是專業的人力資源履歷解析系統。請從以下履歷文字中提取結構化資訊。

候選人姓名：{name}

===履歷文字===
{text[:8000]}
===結束===

請輸出以下 JSON 格式（嚴格只輸出 JSON，不要其他文字）：
{{
  "current_position": "目前或最近職位名稱（例：Senior Backend Engineer）",
  "location": "所在地（例：Taipei City）",
  "skills": "技能清單，逗號分隔，最多20個核心技能（例：Python, Docker, AWS, Golang）",
  "years_experience": "總工作年資（字串數字，例：7）",
  "job_changes": "換工作次數（工作段數-1，字串，例：3）",
  "avg_tenure_months": "平均任職月數（字串，例：24）",
  "recent_gap_months": "最近空窗期月數，若在職填0（字串，例：0）",
  "education": "最高學歷一行描述（例：國立台灣大學 資訊工程學系 學士）",
  "work_history": [
    {{
      "company": "公司名稱",
      "title": "職位名稱",
      "start": "YYYY-MM 或 YYYY",
      "end": "YYYY-MM 或 present",
      "duration_months": 月數整數,
      "description": "詳細工作內容，保留原文所有 bullet points，用 \\n• 分隔每條，盡量完整不省略"
    }}
  ],
  "education_details": [
    {{
      "school": "學校名稱",
      "degree": "學位（學士/碩士/博士/Bachelor/Master等）",
      "major": "科系",
      "start": "YYYY",
      "end": "YYYY"
    }}
  ]
}}

注意：
- 找不到的欄位填空字串 "" 或空陣列 []
- work_history 按時間倒序（最新在前），最多8筆
- description 欄位非常重要：務必把每段工作的所有職責與成就完整提取，不要只寫一句話
- years_experience 從工作起始年計算到2026
- 若為在學學生，recent_gap_months 填 0"""

    try:
        resp = requests.post(
            OPENCLAW_API,
            headers={
                "Authorization": f"Bearer {OPENCLAW_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-sonnet-4-6",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 3000
            },
            timeout=60
        )
        result = resp.json()
        content = result['choices'][0]['message']['content']
        
        # 提取 JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            print(f"  ⚠️  AI 回傳格式異常，改用備用解析")
            return None
    except Exception as e:
        print(f"  ⚠️  AI 解析失敗: {e}，改用備用解析")
        return None


def fallback_extract_info(text, name):
    """備用：規則式解析（AI 失敗時用）"""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    info = {
        "current_position": "",
        "skills": "",
        "education": "",
        "work_history": [],
        "education_details": [],
        "years_experience": "",
        "job_changes": "0",
        "avg_tenure_months": "0",
        "recent_gap_months": "0"
    }
    # Current position
    for l in lines[1:6]:
        if len(l) > 5 and 'LinkedIn' not in l and 'www.' not in l and 'http' not in l:
            info["current_position"] = l
            break
    # Skills
    skills, in_s = [], False
    for line in lines:
        if '熱門技能' in line or 'Top Skills' in line:
            in_s = True; continue
        if in_s:
            if any(s in line for s in ['經歷','Experience','教育','Education']):
                break
            if line and len(line) < 80:
                skills.append(line)
        if len(skills) >= 8:
            break
    info["skills"] = ', '.join(skills[:8])
    # Years estimate
    years = [int(m.group(0)) for m in re.finditer(r'(19|20)\d{2}', text) if 1990 <= int(m.group(0)) <= 2026]
    if years:
        info["years_experience"] = str(max(1, 2026 - min(years)))
    return info


def calculate_stability(info):
    """計算穩定性分數"""
    try:
        avg_tenure = int(info.get('avg_tenure_months', 0) or 0)
        job_changes = int(info.get('job_changes', 0) or 0)
        years = float(info.get('years_experience', 1) or 1)
        gap = int(info.get('recent_gap_months', 0) or 0)
        
        # 維度一：平均任職月數 (50分)
        if avg_tenure >= 36: s1 = 50
        elif avg_tenure >= 24: s1 = 45
        elif avg_tenure >= 18: s1 = 38
        elif avg_tenure >= 12: s1 = 30
        elif avg_tenure >= 6: s1 = 18
        else: s1 = 5
        
        # 維度二：轉職頻率 (30分)
        freq = job_changes / max(years, 1)
        if freq < 0.3: s2 = 30
        elif freq < 0.5: s2 = 25
        elif freq < 0.7: s2 = 18
        elif freq <= 1.0: s2 = 10
        else: s2 = 3
        
        # 維度三：空窗期 (20分)
        if gap == 0: s3 = 20
        elif gap <= 3: s3 = 18
        elif gap <= 6: s3 = 12
        elif gap <= 12: s3 = 6
        else: s3 = 2
        
        return max(20, min(100, s1 + s2 + s3))
    except:
        return 50


def upload_to_drive(pdf_path, candidate_name):
    result = subprocess.run(
        ['gog', 'drive', 'upload', pdf_path,
         '--parent', DRIVE_FOLDER_ID,
         '--account', DRIVE_ACCOUNT],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        output = result.stdout + result.stderr
        id_match = re.search(r'id[:\s]+([A-Za-z0-9_-]{20,})', output)
        if id_match:
            return f"https://drive.google.com/file/d/{id_match.group(1)}/view"
        return "uploaded"
    else:
        print(f"  Drive upload error: {result.stderr[:100]}")
        return None


def upload_to_step1ne(candidate_id, payload):
    try:
        r = requests.patch(f"{API_BASE}/api/candidates/{candidate_id}", json=payload, timeout=15)
        return r.status_code in [200, 201, 204]
    except Exception as e:
        print(f"  API error: {e}")
        return False


def process_candidate(item):
    cid = item['id']
    name = item['name']
    pdf_path = item['pdf']

    if not os.path.exists(pdf_path):
        print(f"❌ {name} - PDF not found: {pdf_path}")
        return False

    # 1. Rename PDF
    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    new_path = os.path.join(os.path.dirname(pdf_path), f"{safe_name}.pdf")
    if not os.path.exists(new_path):
        os.rename(pdf_path, new_path)

    # 2. Upload to Drive
    drive_url = upload_to_drive(new_path, name)
    if drive_url:
        print(f"  ☁️  Drive: {drive_url[:60]}")

    # 3. Parse PDF
    text = parse_pdf(new_path)
    if not text.strip():
        print(f"❌ {name} - Empty PDF")
        return False

    # 4. AI 解析
    print(f"  🤖 AI 解析中...")
    info = ai_extract_info(text, name)
    if not info:
        info = fallback_extract_info(text, name)
        print(f"  ↩️  使用備用解析")

    # 5. 計算穩定性
    stability = calculate_stability(info)

    # 6. 整理 payload
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    notes_parts = [f"PDF解析(AI) {today}"]
    if drive_url and drive_url != "uploaded":
        notes_parts.append(f"履歷連結：{drive_url}")

    payload = {
        "actor": "Jacky-aibot",
        "notes": "\n".join(notes_parts),
        "stability_score": stability,
    }
    
    if info.get('current_position'):
        payload["position"] = info['current_position']
    if info.get('skills'):
        payload["skills"] = info['skills']
    if info.get('education'):
        payload["education"] = info['education']
    if info.get('years_experience'):
        payload["years"] = info['years_experience']
    if info.get('job_changes'):
        payload["jobChanges"] = info['job_changes']
    if info.get('avg_tenure_months'):
        payload["avgTenure"] = info['avg_tenure_months']
    if info.get('recent_gap_months'):
        payload["lastGap"] = info['recent_gap_months']
    if info.get('work_history'):
        payload["work_history"] = info['work_history']      # PATCH 用 snake_case
    if info.get('education_details'):
        payload["education_details"] = info['education_details']  # PATCH 用 snake_case
    if info.get('location'):
        payload["location"] = info['location']

    # 7. Upload to Step1ne
    success = upload_to_step1ne(cid, payload)

    if success:
        os.remove(new_path)
        wh_count = len(info.get('work_history', []))
        skills_count = len([s for s in info.get('skills', '').split(',') if s.strip()])
        print(f"✅ {name} (ID:{cid}) | {info.get('current_position','?')[:35]} | {skills_count} 技能 | {wh_count} 份工作經歷 | 穩定度:{stability} | 已刪除")
        return True
    else:
        print(f"❌ {name} (ID:{cid}) - Step1ne 更新失敗")
        return False


def main():
    mapping_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/pdf_mapping.json'
    
    with open(mapping_file) as f:
        mapping = json.load(f)
    
    print(f"🚀 處理 {len(mapping)} 位候選人履歷（AI 解析版）...")
    print("=" * 60)
    
    success = failed = 0
    for i, item in enumerate(mapping):
        print(f"\n[{i+1}/{len(mapping)}] {item['name']}")
        if process_candidate(item):
            success += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 完成：{success} 成功，{failed} 失敗")


if __name__ == "__main__":
    main()
