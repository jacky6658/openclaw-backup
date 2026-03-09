#!/usr/bin/env python3
"""
LinkedIn 自動發布職缺（匿名版）
- 不顯示公司名稱
- 只發布「招募中」職缺
- 自動從 Google Sheets 讀取
"""

import requests
import subprocess
import sys
import time
from datetime import datetime

def get_linkedin_credentials():
    """讀取 LinkedIn 授權資訊"""
    try:
        with open('/Users/user/clawd/hr-tools/.linkedin_token', 'r') as f:
            access_token = f.read().strip()
        
        with open('/Users/user/clawd/hr-tools/.linkedin_user_id', 'r') as f:
            user_id = f.read().strip()
        
        return access_token, user_id
    except FileNotFoundError:
        print("❌ 請先執行授權流程")
        return None, None

def load_jobs_from_sheets():
    """從 Google Sheets 讀取招募中的職缺"""
    sheet_id = "1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
    
    result = subprocess.run(
        ["gog", "sheets", "get", sheet_id, "A2:L"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 讀取 Google Sheets 失敗: {result.stderr}")
        return []
    
    jobs = []
    lines = result.stdout.strip().split('\n')
    
    for line in lines:
        fields = line.split('|')
        if len(fields) < 10:
            continue
        
        status = fields[9].strip() if len(fields) > 9 else ""
        if status != "招募中":
            continue
        
        # 判斷是否為派遣
        title = fields[0].strip()
        is_dispatch = any(keyword in title.lower() or keyword in fields[6].lower() if len(fields) > 6 else False 
                         for keyword in ["派遣", "dispatch", "contract", "約聘", "外包"])
        
        # 匿名化處理
        job = {
            "title": fields[0].strip(),
            "company": fields[1].strip(),  # 內部記錄用，不會顯示
            "location": fields[3].strip(),
            "salary": fields[4].strip(),
            "skills": fields[5].strip(),
            "description": fields[6].strip() if len(fields) > 6 else "",
            "experience": fields[7].strip() if len(fields) > 7 else "",
            "education": fields[8].strip() if len(fields) > 8 else "",
            "is_dispatch": is_dispatch  # 是否為派遣
        }
        jobs.append(job)
    
    return jobs

def format_anonymous_job_post(job, add_greeting=False):
    """格式化匿名職缺貼文"""
    
    # 產業類型判斷（根據職位名稱）
    industry_hints = {
        "遊戲": "知名遊戲公司",
        "AI": "AI科技公司",
        "工程師": "科技公司",
        "PM": "科技公司",
        "專案": "科技公司",
        "測試": "軟體公司",
        "供應鏈": "製造業集團",
        "會計": "企業集團",
        "QA": "軟體公司"
    }
    
    industry = "知名企業"
    for keyword, hint in industry_hints.items():
        if keyword in job['title']:
            industry = hint
            break
    
    # 節日問候（可選）
    greeting = ""
    if add_greeting:
        import datetime
        now = datetime.datetime.now()
        month = now.month
        day = now.day
        
        # 農曆新年期間（1月底-2月中）
        if month in [1, 2]:
            greeting = "🧧🐍 新年新機會！\n\n"
        # 端午節期間（6月）
        elif month == 6:
            greeting = "🎋 端午佳節，職涯新選擇！\n\n"
        # 中秋節期間（9月）
        elif month == 9:
            greeting = "🥮 中秋佳節，月圓人團圓，事業更上層樓！\n\n"
    
    # 技能列表
    skills_list = job['skills'].split(',') if job['skills'] else []
    skills_text = "\n".join([f"• {skill.strip()}" for skill in skills_list[:5]])
    
    # 經驗與學歷
    requirements = []
    if job['experience']:
        requirements.append(f"• 經驗：{job['experience']}")
    if job['education']:
        requirements.append(f"• 學歷：{job['education']}")
    
    requirements_text = "\n".join(requirements) if requirements else "• 詳細需求請洽獵頭顧問"
    
    # 派遣標注
    dispatch_notice = ""
    if job.get('is_dispatch', False):
        dispatch_notice = "\n⚠️ 此為派遣機會（Contract/Dispatch Position）\n"
    
    # 組成貼文
    post_text = f"""{greeting}🔥【{industry}】{job['title']}
{dispatch_notice}
💰 薪資：{job['salary']}
📍 地點：{job['location']}

📋 技能需求：
{skills_text}

{requirements_text}

💼 有興趣請私訊或留言，我會協助您了解更多！

#招募 #{job['title'].replace(' ', '')} #Step1ne獵頭 #{job['location'].replace(' ', '')}
"""
    
    return post_text

def post_to_linkedin(access_token, user_id, job_text):
    """發布到 LinkedIn"""
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    payload = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": job_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 201

def main():
    """主程式"""
    # 取得授權資訊
    access_token, user_id = get_linkedin_credentials()
    if not access_token:
        return
    
    # 讀取職缺
    print("📋 讀取招募中的職缺...")
    jobs = load_jobs_from_sheets()
    
    if not jobs:
        print("⚠️  目前沒有招募中的職缺")
        return
    
    print(f"找到 {len(jobs)} 個招募中的職缺")
    
    # 發布職缺（限制每天最多 3 個）
    max_posts = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    posted = 0
    
    for i, job in enumerate(jobs[:max_posts]):
        # 第一個職缺加入節日問候
        add_greeting = (i == 0)
        job_text = format_anonymous_job_post(job, add_greeting=add_greeting)
        
        print(f"\n📤 發布職缺：{job['title']} ({job['company']}) - 匿名版")
        print("---")
        print(job_text)
        print("---")
        
        # 詢問確認（測試模式）
        if "--dry-run" in sys.argv:
            print("🔍 Dry-run 模式，不實際發布")
            continue
        
        success = post_to_linkedin(access_token, user_id, job_text)
        
        if success:
            print(f"✅ 已發布：{job['title']}")
            posted += 1
        else:
            print(f"❌ 發布失敗：{job['title']}")
        
        # 避免 API rate limit（每次發布後等 30 秒）
        if posted < max_posts and posted < len(jobs):
            print("⏳ 等待 30 秒...")
            time.sleep(30)
    
    print(f"\n✅ 完成！已發布 {posted} 個職缺到 LinkedIn")

if __name__ == "__main__":
    main()
