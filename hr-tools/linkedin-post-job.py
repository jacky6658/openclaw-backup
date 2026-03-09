#!/usr/bin/env python3
"""
LinkedIn 自動發布職缺
使用 Share on LinkedIn API (w_member_social scope)
"""

import requests
import json
import sys
from datetime import datetime

# LinkedIn OAuth 配置
CLIENT_ID = "86offuzvwvzv8r"
CLIENT_SECRET = "WPL_AP1.a9UnbU0gKid5n8"  # 請從環境變數或安全儲存取得
REDIRECT_URI = "https://oauth.n8n.cloud/oauth2/callback"

# Access Token（需要先透過 OAuth 流程取得）
# 有效期 2 個月，過期後需要重新授權
ACCESS_TOKEN = None  # 第一次執行時需要手動設定

def get_access_token_url():
    """
    生成 OAuth 授權 URL（首次執行時用）
    """
    scope = "openid profile w_member_social email"
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={scope}"
    )
    return auth_url

def exchange_code_for_token(auth_code):
    """
    用授權碼換取 Access Token
    """
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Access Token 已取得")
        print(f"Token: {token_data['access_token']}")
        print(f"有效期: {token_data['expires_in']} 秒 (約 {token_data['expires_in']/86400:.0f} 天)")
        return token_data['access_token']
    else:
        print(f"❌ 取得 Token 失敗: {response.text}")
        return None

def get_user_profile(access_token):
    """
    取得用戶的 LinkedIn ID（用於發布貼文）
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
    if response.status_code == 200:
        profile = response.json()
        user_id = profile['id']
        print(f"✅ LinkedIn ID: {user_id}")
        return user_id
    else:
        print(f"❌ 取得個人資料失敗: {response.text}")
        return None

def post_to_linkedin(access_token, user_id, job_data):
    """
    發布職缺到 LinkedIn
    
    job_data = {
        "title": "職位名稱",
        "company": "公司名稱",
        "location": "地點",
        "salary": "薪資範圍",
        "description": "職缺描述",
        "requirements": ["需求1", "需求2"],
        "apply_url": "應徵連結（可選）"
    }
    """
    
    # 組成貼文內容
    requirements_text = "\n".join([f"• {req}" for req in job_data.get("requirements", [])])
    
    post_text = f"""【{job_data['company']}】{job_data['title']}

💰 薪資：{job_data['salary']}
📍 地點：{job_data['location']}

{job_data.get('description', '')}

📋 需求：
{requirements_text}

有興趣請私訊或投遞履歷！
{job_data.get('apply_url', '')}

#招募 #職缺 #{job_data['title'].replace(' ', '')} #Step1ne獵頭
"""

    # LinkedIn UGC Post API
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
                    "text": post_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print(f"✅ 職缺已發布：{job_data['title']}")
        return True
    else:
        print(f"❌ 發布失敗 ({response.status_code}): {response.text}")
        return False

def load_jobs_from_sheets():
    """
    從 Google Sheets 讀取「招募中」的職缺
    需要先執行 gog sheets API
    """
    import subprocess
    
    # 讀取 step1ne 職缺管理表
    sheet_id = "1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
    
    result = subprocess.run(
        ["gog", "sheets", "get", "--id", sheet_id, "--range", "A2:L"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 讀取 Google Sheets 失敗: {result.stderr}")
        return []
    
    # 解析職缺資料
    jobs = []
    lines = result.stdout.strip().split('\n')
    
    for line in lines:
        fields = line.split('|')
        if len(fields) < 12:
            continue
        
        status = fields[9].strip()  # 狀態欄位
        if status != "招募中":
            continue
        
        job = {
            "title": fields[0].strip(),
            "company": fields[1].strip(),
            "location": fields[3].strip(),
            "salary": fields[4].strip(),
            "description": fields[6].strip(),
            "requirements": fields[5].strip().split(','),  # 技能要求
            "apply_url": fields[10].strip() if len(fields) > 10 else ""
        }
        jobs.append(job)
    
    return jobs

def main():
    """
    主程式
    """
    import os
    
    # 從環境變數或檔案讀取 Access Token
    token_file = "/Users/user/clawd/hr-tools/.linkedin_token"
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            access_token = f.read().strip()
        print("✅ Access Token 已載入")
    else:
        print("⚠️  首次執行，需要先取得 Access Token")
        print("\n步驟 1: 訪問以下網址授權")
        print(get_access_token_url())
        print("\n步驟 2: 授權後會跳轉到 redirect_uri，複製網址中的 code 參數")
        auth_code = input("請貼上 code: ").strip()
        
        access_token = exchange_code_for_token(auth_code)
        if not access_token:
            print("❌ 無法取得 Access Token")
            return
        
        # 儲存 Token
        with open(token_file, 'w') as f:
            f.write(access_token)
        print(f"✅ Token 已儲存到 {token_file}")
    
    # 取得 LinkedIn 用戶 ID
    user_id = get_user_profile(access_token)
    if not user_id:
        print("❌ 無法取得用戶資料")
        return
    
    # 讀取職缺清單
    print("\n📋 讀取職缺清單...")
    jobs = load_jobs_from_sheets()
    print(f"找到 {len(jobs)} 個招募中的職缺")
    
    # 發布職缺（限制每天最多 5 個）
    max_posts = 5
    posted = 0
    
    for job in jobs[:max_posts]:
        print(f"\n發布職缺：{job['company']} - {job['title']}")
        success = post_to_linkedin(access_token, user_id, job)
        if success:
            posted += 1
        
        # 避免 API rate limit（每次發布後等 30 秒）
        if posted < max_posts:
            import time
            time.sleep(30)
    
    print(f"\n✅ 完成！已發布 {posted} 個職缺到 LinkedIn")

if __name__ == "__main__":
    main()
