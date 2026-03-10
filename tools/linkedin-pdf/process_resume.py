#!/usr/bin/env python3
"""
LinkedIn PDF 完整處理流程：
1. 改檔名為人選名稱
2. 上傳 Google Drive (aiagentg888)
3. 解析並匯入 Step1ne（工作經歷+學歷+AI匹配結語）
4. 刪除本地檔案
"""

import json
import subprocess
import re
import requests
import time
import os
import sys

API_BASE = "https://backendstep1ne.zeabur.app"
DRIVE_FOLDER_ID = "1nLVrxKDai3mxdNpNkyjk2tPwRoiyC8eM"  # aiagentg888 候選人履歷
DRIVE_ACCOUNT = "aiagentg888@gmail.com"

def parse_pdf(pdf_path):
    r = subprocess.run(['pdftotext', pdf_path, '-'], capture_output=True, text=True)
    return r.stdout

def extract_info(text, name):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    info = {
        "current_position": "",
        "years_experience": "",
        "skills": "",
        "education": "",
        "educationJson": [],
        "workHistory": [],
        "notes": ""
    }

    # Current position
    for i, line in enumerate(lines[:15]):
        if name.split()[0].lower() in line.lower() or (len(name) > 2 and name[:2] in line):
            for j in range(i+1, min(i+5, len(lines))):
                l = lines[j]
                if len(l) > 5 and not any(s in l for s in ['LinkedIn','www.','http','follower','connection','·']):
                    info["current_position"] = l
                    break
            break
    if not info["current_position"] and len(lines) > 1:
        for l in lines[1:5]:
            if len(l) > 5 and 'LinkedIn' not in l and 'www.' not in l:
                info["current_position"] = l
                break

    # Skills
    skills = []
    in_skills = False
    for line in lines:
        if '熱門技能' in line or 'Top Skills' in line:
            in_skills = True
            continue
        if in_skills:
            if any(s in line for s in ['經歷','Experience','教育','Education','語言','Languages','Certifications','證照','簡介','Summary']):
                break
            if line and len(line) < 80:
                skills.append(line)
        if len(skills) >= 10:
            break
    info["skills"] = ', '.join(skills[:8]) if skills else ""

    # Work history
    in_exp = False
    work_history = []
    current_job = {}
    for line in lines:
        if ('經歷' in line or line == 'Experience') and not in_exp:
            in_exp = True
            continue
        if in_exp:
            if any(s in line for s in ['教育程度','Education','語言','Languages','Top Skills','熱門技能','Certifications']):
                if current_job.get('company') or current_job.get('title'):
                    work_history.append(current_job)
                break
            # Date line detection
            date_match = re.search(r'(19|20)\d{2}', line)
            if date_match and ('-' in line or '至今' in line or 'Present' in line or '年' in line):
                if current_job.get('company') or current_job.get('title'):
                    work_history.append(current_job)
                current_job = {'dates': line, 'title': '', 'company': ''}
            elif current_job.get('dates') and not current_job.get('title'):
                current_job['title'] = line
            elif current_job.get('title') and not current_job.get('company'):
                current_job['company'] = line
        if len(work_history) >= 5:
            break
    if current_job.get('company') or current_job.get('title'):
        work_history.append(current_job)
    info["workHistory"] = work_history[:5]

    # Education
    edu_lines = []
    edu_json = []
    in_edu = False
    for line in lines:
        if '教育程度' in line or (line == 'Education' and not in_edu):
            in_edu = True
            continue
        if in_edu:
            if any(s in line for s in ['語言','Languages','Top Skills','熱門技能','Certifications','經歷','Experience']):
                break
            if line and len(line) < 100:
                edu_lines.append(line)
        if len(edu_lines) >= 6:
            break

    info["education"] = ' | '.join(edu_lines[:3]) if edu_lines else ""

    # Parse edu_json from edu_lines
    if edu_lines:
        school = edu_lines[0] if edu_lines else ''
        degree = edu_lines[1] if len(edu_lines) > 1 else ''
        year_match = re.search(r'(19|20)\d{2}', ' '.join(edu_lines))
        edu_json.append({
            "school": school,
            "degree": degree,
            "year": year_match.group(0) if year_match else None
        })
    info["educationJson"] = edu_json

    # Estimate years
    years_found = [int(m.group(0)) for m in re.finditer(r'(19|20)\d{2}', text) if 1990 <= int(m.group(0)) <= 2026]
    if years_found:
        info["years_experience"] = str(max(1, 2026 - min(years_found)))

    # AI Match Result (basic)
    ai_summary_parts = []
    if info["current_position"]:
        ai_summary_parts.append(f"現職：{info['current_position']}")
    if info["skills"]:
        ai_summary_parts.append(f"核心技能：{info['skills'][:100]}")
    if info["education"]:
        ai_summary_parts.append(f"學歷：{info['education'][:80]}")
    if info["years_experience"]:
        ai_summary_parts.append(f"預估年資：{info['years_experience']}年")

    info["aiMatchResult"] = {
        "summary": " | ".join(ai_summary_parts),
        "source": "PDF解析",
        "parsed_at": time.strftime("%Y-%m-%d")
    }

    info["notes"] = f"PDF解析 {time.strftime('%Y-%m-%d')} | " + " | ".join(ai_summary_parts[:2])

    return info

def upload_to_drive(pdf_path, candidate_name):
    """Upload PDF to Google Drive"""
    result = subprocess.run(
        ['gog', 'drive', 'upload', pdf_path,
         '--parent', DRIVE_FOLDER_ID,
         '--account', DRIVE_ACCOUNT],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        # Try to extract file ID from output
        output = result.stdout + result.stderr
        id_match = re.search(r'id[:\s]+([A-Za-z0-9_-]{20,})', output)
        if id_match:
            file_id = id_match.group(1)
            return f"https://drive.google.com/file/d/{file_id}/view"
        return "uploaded"
    else:
        print(f"  Drive upload error: {result.stderr[:100]}")
        return None

def upload_to_step1ne(candidate_id, info):
    payload = {k: v for k, v in info.items() if v not in ['', [], {}, None]}
    payload["actor"] = "Jacky-aibot"
    try:
        r = requests.patch(f"{API_BASE}/api/candidates/{candidate_id}", json=payload, timeout=10)
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

    # 1. Rename PDF to candidate name
    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    new_path = os.path.join(os.path.dirname(pdf_path), f"{safe_name}.pdf")
    if not os.path.exists(new_path):
        os.rename(pdf_path, new_path)
    
    # 2. Upload to Google Drive
    drive_url = upload_to_drive(new_path, name)
    if drive_url:
        print(f"  ☁️  Drive: {drive_url[:60]}")
    
    # 3. Parse PDF
    text = parse_pdf(new_path)
    if not text.strip():
        print(f"❌ {name} - Empty PDF")
        return False
    
    info = extract_info(text, name)
    if drive_url and drive_url != "uploaded":
        info["resumeLink"] = drive_url

    # 4. Upload to Step1ne
    success = upload_to_step1ne(cid, info)
    
    if success:
        # 5. Delete local file
        os.remove(new_path)
        pos = info.get('current_position', '')[:40]
        skills_count = len([s for s in info.get('skills', '').split(',') if s.strip()])
        print(f"✅ {name} (ID:{cid}) | {pos} | {skills_count} skills | 本地已刪除")
        return True
    else:
        print(f"❌ {name} (ID:{cid}) - Step1ne upload failed")
        return False

def main():
    mapping_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/pdf_mapping.json'
    
    with open(mapping_file) as f:
        mapping = json.load(f)

    print(f"🚀 處理 {len(mapping)} 位候選人履歷...")
    print("=" * 60)

    success = 0
    failed = 0

    for item in mapping:
        name = item['name']
        print(f"\n[{success+failed+1}/{len(mapping)}] {name}")
        if process_candidate(item):
            success += 1
        else:
            failed += 1
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"📊 完成：{success} 成功，{failed} 失敗")

if __name__ == "__main__":
    main()
