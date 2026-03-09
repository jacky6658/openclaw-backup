#!/bin/bash
# HR 招募總覽看板 - 啟動腳本

set -e

echo "🚀 啟動 HR 招募總覽看板..."
echo ""

# 1. 確保資料目錄存在
echo "📁 檢查資料目錄..."
mkdir -p ~/clawd/data/headhunter

# 2. 生成最新看板資料
echo "📊 生成最新看板資料..."
python3 ~/clawd/skills/headhunter/scripts/dashboard.py > /dev/null 2>&1 || {
    echo "⚠️  看板資料生成失敗，將使用空資料"
}

# 3. 啟動 Web 伺服器
echo "🌐 啟動 Web 伺服器..."
cd ~/clawd/projects/hr-dashboard

# 檢查是否已有在運行的實例
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "⚠️  Port 3000 已被占用，嘗試關閉..."
    kill $(lsof -ti:3000) 2>/dev/null || true
    sleep 2
fi

# 啟動開發伺服器
echo ""
echo "✅ 看板已啟動！"
echo ""
echo "📍 本地訪問：  http://localhost:3000"
echo "📍 網路訪問：  http://$(ipconfig getifaddr en0 || echo "N/A"):3000"
echo ""
echo "按 Ctrl+C 停止伺服器"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

npm run dev
