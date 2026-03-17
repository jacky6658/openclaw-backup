#!/usr/bin/env python3
"""Parse LinkedIn PDFs and upload to Step1ne API"""

import json
import subprocess
import re
import requests
import time

API_BASE = "https://api-hr.step1ne.com"

def parse_pdf(pdf_path):
    """Extract text from PDF using pdftotext"""
    r = subprocess.run(['pdftotext', pdf_path, '-'], capture_output=True, text=True)
    return r.stdout

def extract_info(text, name):
    """Extract structured info from LinkedIn PDF text"""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    info = {
        "current_position": "",
        "years_experience": "",
        "skills": "",
        "education": "",
        "work_history": [],
        "notes": ""
    }
    
    # Find current position (usually line 2-4, after name)
    name_found = False
    for i, line in enumerate(lines[:20]):
        if name.lower() in line.lower() or line.lower() in name.lower():
            name_found = True
            # Next meaningful line is usually the position
            for j in range(i+1, min(i+5, len(lines))):
                l = lines[j]
                # Skip location lines (contains · or 台灣/Taiwan/Japan etc)
                if '·' in l or len(l) < 3:
                    continue
                if not any(skip in l for skip in ['LinkedIn', 'www.', 'http', 'contact', 'followers', 'connections']):
                    info["current_position"] = l
                    break
            break
    
    if not info["current_position"] and len(lines) > 1:
        info["current_position"] = lines[1]
    
    # Extract skills (look for 熱門技能 or Top Skills section)
    skills_section = False
    skills = []
    for i, line in enumerate(lines):
        if '熱門技能' in line or 'Top Skills' in line:
            skills_section = True
            continue
        if skills_section:
            if any(stop in line for stop in ['經歷', 'Experience', '教育', 'Education', '語言', 'Languages', 'Certifications', '證照']):
                break
            if line and len(line) < 100 and not line.startswith('·'):
                skills.append(line)
        if len(skills) > 10:
            break
    info["skills"] = ', '.join(skills[:8]) if skills else ""
    
    # Extract education
    edu_section = False
    edu_lines = []
    for i, line in enumerate(lines):
        if '教育程度' in line or 'Education' in line:
            edu_section = True
            continue
        if edu_section:
            if any(stop in line for stop in ['語言', 'Languages', 'Certifications', '證照', '經歷', 'Experience']):
                break
            if line and not line.startswith('·') and len(line) < 100:
                edu_lines.append(line)
        if len(edu_lines) > 5:
            break
    info["education"] = ' | '.join(edu_lines[:3]) if edu_lines else ""
    
    # Extract work history (experience section)
    exp_section = False
    current_job = {}
    work_history = []
    for i, line in enumerate(lines):
        if '經歷' in line or 'Experience' in line:
            exp_section = True
            continue
        if exp_section:
            if any(stop in line for stop in ['教育程度', 'Education', '語言', 'Languages', 'Certifications', '熱門技能', 'Top Skills']):
                if current_job:
                    work_history.append(current_job)
                break
            # Date patterns like "Jan 2020 - Present" or "2020年 - 現在"
            date_pattern = r'(\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
            if re.search(date_pattern, line) and ('至今' in line or 'Present' in line or '-' in line or '年' in line):
                if current_job.get('company'):
                    work_history.append(current_job)
                current_job = {"dates": line}
            elif current_job.get('dates') and not current_job.get('title'):
                current_job['title'] = line
            elif current_job.get('title') and not current_job.get('company'):
                current_job['company'] = line
        if len(work_history) >= 5:
            break
    if current_job and current_job.get('company'):
        work_history.append(current_job)
    
    info["work_history"] = work_history[:5]
    
    # Estimate years of experience from work history dates
    years_est = estimate_years(text)
    info["years_experience"] = str(years_est) if years_est else ""
    
    # Build notes summary
    notes_parts = []
    if info["current_position"]:
        notes_parts.append(f"現職：{info['current_position']}")
    if info["skills"]:
        notes_parts.append(f"技能：{info['skills'][:100]}")
    if info["education"]:
        notes_parts.append(f"學歷：{info['education'][:80]}")
    if info["years_experience"]:
        notes_parts.append(f"年資估計：{info['years_experience']}年")
    info["notes"] = " | ".join(notes_parts)
    
    return info

def estimate_years(text):
    """Estimate total years of experience from PDF text"""
    years_found = []
    for match in re.finditer(r'(19|20)(\d{2})', text):
        yr = int(match.group(0))
        if 1990 <= yr <= 2026:
            years_found.append(yr)
    if years_found:
        oldest = min(years_found)
        return max(1, 2026 - oldest)
    return None

def upload_to_step1ne(candidate_id, info, name):
    """Upload parsed info to Step1ne API"""
    url = f"{API_BASE}/api/candidates/{candidate_id}"
    payload = {
        "current_position": info.get("current_position", ""),
        "years_experience": info.get("years_experience", ""),
        "skills": info.get("skills", ""),
        "education": info.get("education", ""),
        "work_history": info.get("work_history", []),
        "notes": info.get("notes", ""),
        "actor": "Jacky-aibot"
    }
    # Remove empty fields
    payload = {k: v for k, v in payload.items() if v != "" and v != [] or k == "actor"}
    
    try:
        r = requests.patch(url, json=payload, timeout=10)
        return r.status_code in [200, 201, 204]
    except Exception as e:
        print(f"  Upload error: {e}")
        return False

def main():
    with open('/tmp/pdf_mapping.json') as f:
        mapping = json.load(f)
    
    success = 0
    failed = 0
    
    print(f"🔍 Parsing and uploading {len(mapping)} PDFs to Step1ne...")
    print("=" * 50)
    
    for item in mapping:
        cid = item['id']
        name = item['name']
        pdf_path = item['pdf']
        
        try:
            text = parse_pdf(pdf_path)
            if not text.strip():
                print(f"❌ {name} - Empty PDF")
                failed += 1
                continue
            
            info = extract_info(text, name)
            
            if upload_to_step1ne(cid, info, name):
                pos = info.get('current_position', '')[:40]
                skills_count = len([s for s in info.get('skills', '').split(',') if s.strip()])
                print(f"✅ {name} (ID:{cid}) | {pos} | {skills_count} skills")
                success += 1
            else:
                print(f"❌ {name} (ID:{cid}) - Upload failed")
                failed += 1
        except Exception as e:
            print(f"❌ {name} (ID:{cid}) - Error: {e}")
            failed += 1
        
        time.sleep(0.3)
    
    print("=" * 50)
    print(f"📊 Done: {success} uploaded, {failed} failed out of {len(mapping)}")
    
    # Summary of failed downloads (not in mapping)
    all_ids = {"1358","1360","1364","1365","1373","1377","1378","1383","1384",
               "1509","1510","1520","1521","1522","1523","1524","1532","1533",
               "1534","1535","1536","1537","1538","1539","1540","1541","1542",
               "1543","1544","1545","1546","1547","1548","1620"}
    mapped_ids = {item['id'] for item in mapping}
    skipped_ids = all_ids - mapped_ids
    if skipped_ids:
        print(f"\n⚠️  PDF 下載失敗（需手動補充）: {len(skipped_ids)} 位")
        candidates_map = {str(c['id']): c['name'] for c in json.load(open('/tmp/li_candidates.json'))}
        for sid in sorted(skipped_ids):
            print(f"  • {candidates_map.get(sid, sid)} (ID:{sid})")

if __name__ == "__main__":
    main()
