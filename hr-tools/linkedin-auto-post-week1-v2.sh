#!/bin/bash
# LinkedIn 自動發布腳本 - Week 1 v2 (2025.02.17-02.23)
# 修正版：今天已發除夕問候 + .NET職缺

cd /Users/user/clawd/hr-tools

# 讀取 Token
ACCESS_TOKEN=$(cat .linkedin_token)
USER_ID=$(cat .linkedin_user_id)

# 發布函數
post_to_linkedin() {
    local post_text="$1"
    
    python3 << PYTHON_EOF
import requests
import json

access_token = "$ACCESS_TOKEN"
user_id = "$USER_ID"
post_text = """$post_text"""

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
    print("✅ 貼文已發布！")
else:
    print(f"❌ 發布失敗: {response.text}")
PYTHON_EOF
}

# 貼文內容
case "$1" in
    "1")
        # 週一 2/17（初一）- 新年快樂
        POST_TEXT='🐍 蛇年行大運！初一快樂！

新年第一天，祝大家：
✨ 工作順利，步步高升
✨ 薪水翻倍，財源廣進
✨ 遇到貴人，機會滿滿

───────────────────

💬 新年小調查：

你今年最想實現的職涯目標是什麼？

A. 升職加薪 💰
B. 轉換跑道 🔄
C. 學習新技能 📚
D. 找到 work-life balance ⚖️

留言告訴我！👇

#蛇年 #初一 #新年快樂 #職涯目標 #Step1ne獵頭'
        echo "📅 發布貼文 1：初一快樂"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "2")
        # 週二 2/18（初二）- PM 職缺
        POST_TEXT='💡 為什麼這個 PM 職缺不一樣？

大部分 PM 做的是「接需求、排優先級」
但這個職缺，你會做的是「定義產品方向」

🚀 你將獲得：

✅ 策略思維
• 從 0 到 1 打造新產品
• 直接與創辦人討論產品策略
• 影響公司未來方向

✅ 薪資成長
• 起薪：90k - 140k（比市場高 20%）
• 股票選擇權
• 產品成功 → 你的價值翻倍

✅ 團隊文化
• 扁平化，沒有層層審批
• Data-driven decision
• AI/SaaS 產業的創新環境

───────────────────

📍 地點：台北市
🏢 產業：知名科技公司

💼 如果你想要的不只是「一份工作」，而是「職涯突破」
歡迎私訊我，讓我們聊聊這個機會！

#產品經理 #職涯突破 #PM #Step1ne獵頭 #台北職缺'
        echo "📅 發布貼文 2：PM 職缺"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "3")
        # 週三 2/19（初三）- 談薪技巧
        POST_TEXT='💰 如何談到更高的薪水？5 個實戰技巧

作為獵頭，我每週協助候選人談薪資。
以下是最有效的 5 招：

1️⃣ 做功課
面試前查市場行情（例：.NET Senior 平均 120k）
知道底線，才能談判

2️⃣ 展示價值
別只說「我想要 XX 薪水」
改說「我曾帶團隊做 XX 專案，節省 30% 成本」

3️⃣ 問對問題
「這個職位的薪資範圍是多少？」
不是「你們能給我多少？」

4️⃣ 不要第一個報價
讓對方先說 → 你才知道天花板在哪

5️⃣ 留談判空間
期望薪資不要只說一個數字
說範圍：「100k - 120k，依整體 package 而定」

───────────────────

💡 記住：薪資談判不是對抗，是合作。
雙方都想找到 win-win 的點。

你有用過哪些談薪技巧？留言分享！👇

#薪資談判 #職涯建議 #工程師 #Step1ne獵頭'
        echo "📅 發布貼文 3：談薪技巧"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "4")
        # 週四 2/20（初四）- 技能趨勢
        POST_TEXT='🚀 2025 最夯技能是什麼？

分析 1000+ 職缺後發現：

📈 需求暴增：

   #1  Go         ⬆️ +33%
   #2  Rust       ⬆️ +40%
   #3  Python     ⬆️ +12%
   #4  .NET       ⬆️ +14%

📉 需求下降：

   #5  Java       ⬇️ -4%
   #6  JavaScript ⬇️ -2%

───────────────────

💡 給工程師的建議：

• 已經會 Java？考慮加學 Go
• 前端出身？學 Python 做全端
• 想高薪？Rust 人才缺口大

你正在學什麼新技能？留言分享！👇

#技術趨勢 #職涯規劃 #工程師成長 #Step1ne獵頭'
        echo "📅 發布貼文 4：技能趨勢"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "5")
        # 週五 2/21（初五）- 供應鏈職缺
        POST_TEXT='🌏 想挑戰高薪 + 海外歷練？這個機會不容錯過！

【知名製造業集團】供應鏈管理部 協理/副總

💰 薪資：150,000 - 300,000 TWD/月
📍 地點：柬埔寨金邊（外派）
🏢 產業：醫療器材製造業

🎯 你將負責：
• 跨國供應鏈管理與優化
• 採購策略制定與執行
• 物流規劃與成本控制
• 建立 ERP 系統流程

📋 我們在找：
• 15年以上供應鏈管理經驗
• 熟悉國際採購與物流
• 優秀的跨部門溝通能力
• 英文流利（工作語言）

✨ 為什麼值得考慮？
• 薪資遠高於台灣市場
• 完整外派福利（住宿、機票、保險）
• 快速升遷機會
• 國際化工作經驗

💼 想了解更多？私訊我！

#供應鏈管理 #海外工作 #高階主管 #Step1ne獵頭'
        echo "📅 發布貼文 5：供應鏈職缺"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "6")
        # 週六 2/22（初六）- 互動遊戲
        POST_TEXT='🎮 週末遊戲時間！

如果你是 RPG 角色，你的職業是什麼？

🗡️ 戰士 - Frontend（直接面對用戶）
🏹 遊俠 - Backend（遠程支援）
🧙 法師 - Data Scientist（魔法分析）
🛡️ 坦克 - DevOps（守護系統）
💼 商人 - PM（資源協調）
🎨 工匠 - Designer（打造體驗）

留言告訴我你的職業 + 等級！
例：「🗡️ 戰士 Lv.5（React 5年）」

───────────────────

週末愉快！💪
下週繼續聊職涯成長！

#週末 #工程師 #遊戲化 #Step1ne獵頭'
        echo "📅 發布貼文 6：週末互動"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    *)
        echo "使用方式："
        echo "  ./linkedin-auto-post-week1-v2.sh 1  # 週一（初一）"
        echo "  ./linkedin-auto-post-week1-v2.sh 2  # 週二（PM職缺）"
        echo "  ./linkedin-auto-post-week1-v2.sh 3  # 週三（談薪）"
        echo "  ./linkedin-auto-post-week1-v2.sh 4  # 週四（趨勢）"
        echo "  ./linkedin-auto-post-week1-v2.sh 5  # 週五（供應鏈）"
        echo "  ./linkedin-auto-post-week1-v2.sh 6  # 週六（互動）"
        ;;
esac
