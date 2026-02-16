#!/bin/bash
# Threads OAuth 授權流程

source .env

echo "🔐 Threads OAuth 授權"
echo ""
echo "步驟 1: 請在瀏覽器中打開以下網址進行授權："
echo ""
echo "https://threads.net/oauth/authorize?client_id=${THREADS_APP_ID}&redirect_uri=${THREADS_REDIRECT_URI}&scope=threads_basic,threads_content_publish&response_type=code"
echo ""
echo "授權後，你會被重定向到一個頁面。"
echo "請複製 URL 中的 'code=' 後面的內容（授權碼）。"
echo ""
read -p "請輸入授權碼: " AUTH_CODE

echo ""
echo "步驟 2: 取得 Access Token..."

# 取得短期 Access Token
RESPONSE=$(curl -s -X POST "https://graph.threads.net/oauth/access_token" \
  -F "client_id=${THREADS_APP_ID}" \
  -F "client_secret=${THREADS_APP_SECRET}" \
  -F "grant_type=authorization_code" \
  -F "redirect_uri=${THREADS_REDIRECT_URI}" \
  -F "code=${AUTH_CODE}")

echo "$RESPONSE" | jq .

SHORT_TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
USER_ID=$(echo "$RESPONSE" | jq -r '.user_id')

if [ "$SHORT_TOKEN" = "null" ]; then
  echo "❌ 取得 Token 失敗！"
  echo "$RESPONSE"
  exit 1
fi

echo ""
echo "✅ 短期 Token 取得成功！"
echo "User ID: $USER_ID"

# 轉換為長期 Access Token
echo ""
echo "步驟 3: 轉換為長期 Access Token..."

LONG_RESPONSE=$(curl -s -X GET "https://graph.threads.net/access_token?grant_type=th_exchange_token&client_secret=${THREADS_APP_SECRET}&access_token=${SHORT_TOKEN}")

echo "$LONG_RESPONSE" | jq .

LONG_TOKEN=$(echo "$LONG_RESPONSE" | jq -r '.access_token')
EXPIRES_IN=$(echo "$LONG_RESPONSE" | jq -r '.expires_in')

if [ "$LONG_TOKEN" = "null" ]; then
  echo "❌ 轉換失敗！"
  echo "$LONG_RESPONSE"
  exit 1
fi

echo ""
echo "✅ 長期 Token 取得成功！"
echo "有效期限: $EXPIRES_IN 秒 (約 $(($EXPIRES_IN / 86400)) 天)"

# 儲存設定
cat > config.json << JSONEOF
{
  "app_id": "${THREADS_APP_ID}",
  "user_id": "${USER_ID}",
  "access_token": "${LONG_TOKEN}",
  "expires_at": $(date -v +60d +%s),
  "created_at": $(date +%s)
}
JSONEOF

chmod 600 config.json

echo ""
echo "✅ 設定已儲存到 config.json"
echo ""
echo "🎉 OAuth 授權完成！現在可以發文了！"
