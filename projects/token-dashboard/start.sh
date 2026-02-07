#!/bin/bash

# OpenClaw Token Dashboard - 快速啟動腳本
# 使用方法: ./start.sh

clear
echo "⚡🦞 OpenClaw Token Dashboard v2.0"
echo "===================================="
echo "🌃 Cyberpunk Theme - Neon Future Tech"
echo "===================================="
echo ""

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 錯誤：未安裝 Node.js"
    echo "請先安裝 Node.js: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js 版本: $(node -v)"

# 檢查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "❌ 錯誤：未安裝 OpenClaw"
    echo "請先安裝 OpenClaw"
    exit 1
fi

echo "✅ OpenClaw 已安裝"

# 檢查 Gateway 狀態
echo ""
echo "📡 檢查 Gateway 狀態..."
if openclaw status | grep -q "Gateway.*running"; then
    echo "✅ Gateway 運行中"
else
    echo "⚠️  Gateway 未運行，嘗試啟動..."
    openclaw gateway start
    sleep 2
    if openclaw status | grep -q "Gateway.*running"; then
        echo "✅ Gateway 啟動成功"
    else
        echo "❌ Gateway 啟動失敗，請手動檢查"
    fi
fi

# 啟動伺服器
echo ""
echo "🚀 正在啟動 Token Dashboard..."
echo "===================================="
echo ""
echo "🌌 主題配色："
echo "   • 霓虹粉 (#ff0080) - 主按鈕"
echo "   • 電光藍 (#00f0ff) - 標籤邊框"
echo "   • 螢光綠 (#00ff88) - 成功狀態"
echo ""
echo "📊 Dashboard URL: http://localhost:3737"
echo ""
echo "⚡ 特色："
echo "   ✨ 1秒即時刷新"
echo "   🔄 一鍵切換模型"
echo "   🌃 賽博朋克霓虹特效"
echo ""
echo "按 Ctrl+C 停止伺服器"
echo "===================================="
echo ""

cd "$(dirname "$0")"
node backend/server.js
