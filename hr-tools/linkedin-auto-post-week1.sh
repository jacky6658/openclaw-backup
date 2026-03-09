#!/bin/bash
# LinkedIn 自動發布腳本 - Week 1 (2025.02.17-02.23)
# 使用方式：./linkedin-auto-post-week1.sh [post_number]

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
        # 週一 2/17 - 新年問候
        POST_TEXT='🧧🐍 蛇年快樂！新年新開始！

過去一年，你在職涯上有什麼收穫？
新的一年，你想要什麼改變？

留言分享你的 2025 職涯目標，
我會選 3 位送出「履歷健檢」服務！🎁

祝大家新年快樂，工作順利，薪水翻倍！✨

#蛇年 #新年快樂 #職涯目標 #Step1ne獵頭'
        echo "📅 發布貼文 1：新年問候"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "2")
        # 週二 2/18 - .NET 工程師職缺（故事型）
        POST_TEXT='還記得你第一次拿到 offer 的心情嗎？

那種「終於被認可」的感覺，
那種「未來充滿可能」的期待。

但三年過去了，你還在同一個位置嗎？

🔥 如果你準備好迎接新挑戰...

【知名遊戲公司】.NET工程師

💰 薪資：80,000 - 120,000 TWD/月
📍 地點：台北市內湖區
👥 需求：3 人

📋 我們在找：
• .NET Core / .NET Framework 3年以上實戰經驗
• SQL Server、Entity Framework
• RESTful API 設計能力
• Git 版本控制

✨ 加分項目：
• 遊戲產業經驗
• 微服務架構經驗
• Azure 或 AWS 雲端服務

這不只是一份工作，
這是你職涯的下一個里程碑。

💼 準備好了嗎？私訊我，讓我們聊聊你的下一步。

#職涯成長 #新挑戰 #NET工程師 #Step1ne獵頭 #台北職缺'
        echo "📅 發布貼文 2：.NET 工程師職缺"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "3")
        # 週三 2/19 - 職涯建議（談薪技巧）
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
        # 週四 2/20 - PM 職缺（價值型）
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
        echo "📅 發布貼文 4：PM 職缺"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "5")
        # 週五 2/21 - 技能趨勢
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
        echo "📅 發布貼文 5：技能趨勢"
        post_to_linkedin "$POST_TEXT"
        ;;
        
    "6")
        # 週六 2/22 - 互動遊戲
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
        echo "  ./linkedin-auto-post-week1.sh 1  # 發布貼文 1（週一）"
        echo "  ./linkedin-auto-post-week1.sh 2  # 發布貼文 2（週二）"
        echo "  ./linkedin-auto-post-week1.sh 3  # 發布貼文 3（週三）"
        echo "  ./linkedin-auto-post-week1.sh 4  # 發布貼文 4（週四）"
        echo "  ./linkedin-auto-post-week1.sh 5  # 發布貼文 5（週五）"
        echo "  ./linkedin-auto-post-week1.sh 6  # 發布貼文 6（週六）"
        ;;
esac
