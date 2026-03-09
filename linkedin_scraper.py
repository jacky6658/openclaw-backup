#!/usr/bin/env python3
"""
LinkedIn Profile Scraper via Chrome JS extraction
- Opens each LinkedIn profile in Chrome
- Extracts text via JavaScript (no OCR)
- Parses work history, education, skills
- PATCHes Step1ne API with structured data
"""

import subprocess, os, time, json, re, requests

BACKEND = "https://backendstep1ne.zeabur.app"
ACTOR = "Jacky-aibot"
WORKDIR = os.path.expanduser("~/Desktop/li_scrape")
os.makedirs(WORKDIR, exist_ok=True)

def navigate_chrome(url):
    script = f'''
tell application "Google Chrome"
    activate
    set URL of active tab of front window to "{url}"
end tell
'''
    subprocess.run(['osascript', '-e', script], capture_output=True)
    time.sleep(6)

def scroll_page():
    """Scroll through page to trigger lazy loading"""
    script = '''
tell application "Google Chrome"
    activate
end tell
'''
    subprocess.run(['osascript', '-e', script], capture_output=True)
    time.sleep(0.5)
    for _ in range(6):
        subprocess.run(['peekaboo', 'scroll', '--app', 'Google Chrome',
                       '--direction', 'down', '--amount', '8'], capture_output=True)
        time.sleep(1.2)
    time.sleep(1)

def get_page_text():
    """Extract full page text via Chrome JavaScript"""
    js = "document.body.innerText"
    script = f'''
tell application "Google Chrome"
    set pageText to execute active tab of front window javascript "{js}"
    return pageText
end tell
'''
    result = subprocess.run(['osascript', '-e', script],
                           capture_output=True, text=True)
    return result.stdout.strip()

def parse_profile(text, linkedin_url):
    """Parse page text into structured data"""
    data = {}
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # --- Location ---
    loc_m = re.search(
        r'\b(Taipei|Taichung|Kaohsiung|Hsinchu|Tainan|New Taipei|Taoyuan|'
        r'Keelung|Yilan|Taitung|Hualien|Nantou|Chiayi|Yunlin|Changhua|'
        r'Miaoli|Pingtung|Taiwan)(?:\s+City(?:\s+\S+)?)?\b',
        text, re.IGNORECASE)
    if loc_m:
        data['location'] = loc_m.group(0).strip()

    # --- Email ---
    email_m = re.search(r'\b[\w.\-]+@[\w.\-]+\.(com|org|edu|tw|net|io)\b', text, re.I)
    if email_m:
        em = email_m.group(0).lower()
        if not any(s in em for s in ['linkedin', 'noreply', 'example']):
            data['email'] = em

    # --- Phone ---
    phone_m = re.search(
        r'(?:\+886[-\s]?|0)(?:9\d{2}[-\s]?\d{3}[-\s]?\d{3}|\d{1,2}[-\s]?\d{4}[-\s]?\d{4})',
        text)
    if phone_m:
        data['phone'] = phone_m.group(0)

    # --- Work History (structured) ---
    work_history = parse_work_history(lines)
    if work_history:
        data['workHistory'] = work_history
        # Also set position from most recent job
        if not data.get('position') and work_history:
            data['position'] = work_history[0].get('title', '')

    # --- Education (structured) ---
    education_json = parse_education(lines)
    if education_json:
        data['educationJson'] = education_json
        # Also set text education field
        if education_json:
            e = education_json[0]
            parts = [p for p in [e.get('degree'), e.get('major'), e.get('school')] if p]
            data['education'] = ', '.join(parts)

    # --- Skills ---
    skills = parse_skills(text)
    if skills:
        data['skills'] = skills

    return data

def parse_work_history(lines):
    """Parse work history from page lines"""
    work_items = []
    
    # Find "Experience" section
    exp_start = -1
    for i, l in enumerate(lines):
        if re.match(r'^Experience$', l, re.I):
            exp_start = i
            break
    
    if exp_start == -1:
        return []

    # Find end of experience section (next major section)
    section_headers = re.compile(
        r'^(Education|Skills|Certifications|Licenses|Publications|'
        r'Volunteer|Languages|Accomplishments|Interests|Activity|People also|'
        r'More profiles)$', re.I)
    
    exp_lines = []
    for i in range(exp_start + 1, len(lines)):
        if section_headers.match(lines[i]):
            break
        exp_lines.append(lines[i])

    # Parse individual jobs
    # Pattern: job title, company, period, [description]
    i = 0
    while i < len(exp_lines):
        l = exp_lines[i]
        
        # Period pattern: "Jan 2020 – Present" or "2015 - 2020"
        period_m = re.search(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|'
            r'\d{4})\s*[–\-]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
            r'\s+\d{4}|Present|\d{4})',
            l, re.I)
        
        if period_m:
            period = period_m.group(0)
            # Look back for title and company
            title = exp_lines[i-2].strip() if i >= 2 else ''
            company = exp_lines[i-1].strip() if i >= 1 else ''
            
            # Look forward for description
            desc_parts = []
            j = i + 1
            while j < len(exp_lines) and j < i + 6:
                nl = exp_lines[j].strip()
                if re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|\d{4})\s*[–\-]', nl):
                    break
                if nl and len(nl) > 10 and not re.match(r'^\d+\s*(mos?|yrs?|years?|months?)', nl, re.I):
                    desc_parts.append(nl)
                j += 1

            if title and company and len(title) > 2 and len(company) > 2:
                # Clean up duration lines (e.g. "2 yrs 3 mos") from title/company
                if not re.match(r'^\d+\s*(mos?|yrs?|years?|months?)', title, re.I) and \
                   not re.match(r'^\d+\s*(mos?|yrs?|years?|months?)', company, re.I):
                    work_items.append({
                        'title': title,
                        'company': company,
                        'period': period,
                        'description': ' '.join(desc_parts[:2])
                    })
        i += 1

    return work_items[:8]  # Max 8 jobs

def parse_education(lines):
    """Parse education from page lines"""
    edu_items = []

    # Find "Education" section
    edu_start = -1
    for i, l in enumerate(lines):
        if re.match(r'^Education$', l, re.I):
            edu_start = i
            break

    if edu_start == -1:
        return []

    section_headers = re.compile(
        r'^(Skills|Certifications|Experience|Languages|Volunteer|Activity|'
        r'Accomplishments|People also|More profiles)$', re.I)

    edu_lines = []
    for i in range(edu_start + 1, len(lines)):
        if section_headers.match(lines[i]):
            break
        edu_lines.append(lines[i])

    # Parse schools
    i = 0
    while i < len(edu_lines):
        l = edu_lines[i]
        # Year pattern
        year_m = re.search(r'(\d{4})\s*[–\-]\s*(\d{4}|Present)', l, re.I)
        
        if year_m:
            school = edu_lines[i-2].strip() if i >= 2 else ''
            degree_major = edu_lines[i-1].strip() if i >= 1 else ''
            
            # Parse degree and major from "Bachelor of Science, Computer Science"
            degree, major = '', ''
            dm = re.match(r'(Bachelor|Master|MBA|PhD|M\.S\.|B\.S\.|B\.A\.|M\.A\.|Doctor)[^,\n]*,?\s*(.*)', degree_major, re.I)
            if dm:
                degree = dm.group(1)
                major = dm.group(2).strip()
            else:
                major = degree_major

            if school and len(school) > 2:
                edu_items.append({
                    'school': school,
                    'degree': degree or None,
                    'major': major or None,
                    'year': year_m.group(2) if year_m.group(2) != 'Present' else None
                })
        i += 1

    return edu_items[:4]  # Max 4 education entries

def parse_skills(text):
    """Extract skills from page text"""
    skills_m = re.search(r'(?:Top skills?|Skills?)[:\s\n]+(.{20,400}?)(?:\n\n|\Z)',
                         text, re.I | re.S)
    if skills_m:
        raw = skills_m.group(1)
        skills = re.findall(r'([A-Z][A-Za-z\+#\. ]{2,35})', raw)
        skills = [s.strip() for s in skills if len(s.strip()) > 2]
        if skills:
            return ', '.join(skills[:15])
    return ''

def get_crawler_candidates():
    """Get all Crawler-WebUI candidates with LinkedIn URLs"""
    r = requests.get(f"{BACKEND}/api/candidates?limit=2000", timeout=15)
    candidates = r.json().get('data', [])
    result = []
    for c in candidates:
        if 'Crawler-WebUI' not in (c.get('recruiter') or ''):
            continue
        url = c.get('linkedinUrl') or c.get('linkedin_url', '')
        if 'linkedin.com' in str(url):
            result.append({
                'id': c['id'],
                'name': c['name'],
                'url': url,
            })
    return result

def patch_candidate(cid, data):
    """Update candidate in Step1ne"""
    payload = {'by': ACTOR}
    flat_fields = ['email', 'phone', 'location', 'education', 'position', 'skills']
    for f in flat_fields:
        if data.get(f):
            payload[f] = data[f]

    # Structured arrays
    if data.get('workHistory'):
        payload['workHistory'] = data['workHistory']
    if data.get('educationJson'):
        payload['educationJson'] = data['educationJson']

    if len(payload) <= 1:
        return False, "nothing to update"

    r = requests.patch(f"{BACKEND}/api/candidates/{cid}", json=payload, timeout=10)
    return r.status_code in [200, 201, 204], r.text[:200]

def process_one(candidate):
    """Process a single LinkedIn profile"""
    cid = candidate['id']
    name = candidate['name']
    url = candidate['url']

    print(f"\n{'='*50}")
    print(f"[{name}] (ID:{cid})")
    print(f"URL: {url}")

    # Navigate and wait
    navigate_chrome(url)

    # Scroll to load lazy content
    scroll_page()

    # Extract text via JS
    text = get_page_text()
    
    # Save raw text for debugging
    with open(os.path.join(WORKDIR, f'raw_{cid}.txt'), 'w', encoding='utf-8') as f:
        f.write(text)

    # Check if we hit a sign-in wall
    if 'Sign in' in text[:200] or len(text) < 200:
        print(f"  ⚠️  Sign-in wall or empty page, skipping")
        return {'id': cid, 'name': name, 'skipped': True}

    # Parse
    extracted = parse_profile(text, url)
    print(f"  Extracted: {json.dumps(extracted, ensure_ascii=False, indent=4)}")

    # Patch
    ok, msg = patch_candidate(cid, extracted)
    print(f"  PATCH: {'✅' if ok else '❌'} {msg[:100]}")

    return {'id': cid, 'name': name, 'extracted': extracted, 'patched': ok}

if __name__ == '__main__':
    import sys

    print("=== LinkedIn Profile Scraper (JS mode) ===")
    candidates = get_crawler_candidates()
    print(f"Found {len(candidates)} Crawler-WebUI candidates with LinkedIn")

    batch = 5
    run_all = '--all' in sys.argv
    if not run_all:
        if '--batch' in sys.argv:
            idx = sys.argv.index('--batch')
            batch = int(sys.argv[idx+1]) if idx+1 < len(sys.argv) else 5
        # Skip offset support
        offset = 0
        if '--offset' in sys.argv:
            oi = sys.argv.index('--offset')
            offset = int(sys.argv[oi+1]) if oi+1 < len(sys.argv) else 0
        candidates = candidates[offset:offset+batch]
        print(f"BATCH MODE: {len(candidates)} candidates (offset={offset})")

    results, failed = [], []
    for i, cand in enumerate(candidates):
        print(f"\n[{i+1}/{len(candidates)}]", flush=True)
        try:
            r = process_one(cand)
            results.append(r)
            if i < len(candidates) - 1:
                delay = 10 if run_all else 8
                print(f"  Waiting {delay}s...")
                time.sleep(delay)
        except Exception as e:
            print(f"  ERROR: {e}")
            failed.append({'id': cand['id'], 'name': cand['name'], 'error': str(e)})

    print(f"\n{'='*50}")
    print(f"=== DONE: {len(results)} processed, {len(failed)} failed ===")
    patched = sum(1 for r in results if r.get('patched'))
    print(f"Successfully updated: {patched}/{len(results)}")
    if failed:
        for f in failed:
            print(f"  FAILED: {f['name']} - {f['error']}")

    summary_path = os.path.join(WORKDIR, 'summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({'results': results, 'failed': failed}, f, ensure_ascii=False, indent=2)
    print(f"Summary: {summary_path}")
