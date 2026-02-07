#!/bin/bash

# OpenClaw Token Dashboard - 圖形化啟動器
# 雙擊此檔案即可啟動 Dashboard

# 獲取腳本所在目錄
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 清除終端
clear

# 顯示美化的啟動畫面
echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║        ⚡ OpenClaw Token Dashboard v2.0 ⚡          ║"
echo "║        🌃 Cyberpunk Theme - Neon Future Tech        ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "🚀 正在啟動..."
echo ""

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 錯誤：未安裝 Node.js"
    echo ""
    echo "請先安裝 Node.js: https://nodejs.org/"
    echo ""
    read -p "按 Enter 鍵關閉視窗..."
    exit 1
fi

echo "✅ Node.js: $(node -v)"

# 檢查 node_modules
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 首次啟動，正在安裝依賴..."
    npm install
    echo ""
fi

# 檢查並清理舊的 Dashboard 進程
echo "🔍 檢查舊進程..."
if lsof -i :3737 &> /dev/null; then
    echo "⚠️  發現舊的 Dashboard 進程，正在清理..."
    pkill -f "node.*server.js" 2>/dev/null
    sleep 2
    echo "✅ 清理完成"
fi

# 檢查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "⚠️  警告：未偵測到 OpenClaw"
    echo "   Dashboard 仍可啟動，但部分功能可能無法使用"
    echo ""
else
    echo "✅ OpenClaw: 已安裝"
    
    # 檢查並自動啟動 Gateway
    if pgrep -f "openclaw-gateway" &> /dev/null; then
        echo "✅ Gateway: 運行中"
    else
        echo "⚠️  Gateway: 未運行"
        echo "🔧 正在自動啟動 Gateway..."
        
        # 嘗試啟動 Gateway
        if openclaw gateway start &> /dev/null; then
            sleep 2
            
            # 驗證是否啟動成功
            if pgrep -f "openclaw-gateway" &> /dev/null; then
                echo "✅ Gateway: 已自動啟動"
            else
                echo "⚠️  Gateway: 啟動失敗"
                echo "   請手動執行: openclaw gateway start"
            fi
        else
            echo "⚠️  無法啟動 Gateway"
            echo "   Dashboard 仍可使用，但模型切換功能將無法使用"
        fi
        echo ""
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                    訪問資訊                          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 獲取本機 IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)

echo "💻 本機訪問："
echo "   http://localhost:3737"
echo ""
echo "📱 手機訪問（同 WiFi）："
if [ -n "$LOCAL_IP" ]; then
    echo "   http://$LOCAL_IP:3737"
    echo ""
    echo "   📸 用手機相機掃描 QR Code："
    echo "   https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=http://$LOCAL_IP:3737"
else
    echo "   無法自動偵測 IP，請手動查詢："
    echo "   系統偏好設定 > 網路 > WiFi > IP 位址"
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                    Dashboard 功能                     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "✨ 1 秒即時刷新監控"
echo "🔄 一鍵切換 AI 模型"
echo "📊 Token 用量統計"
echo "💰 成本分析"
echo "📱 完整手機響應式"
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              正在啟動伺服器...                        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "⏳ 請稍候..."
sleep 2

# 啟動伺服器
echo ""
echo "🎉 Dashboard 已啟動！"
echo ""
echo "📍 請在瀏覽器中開啟上方網址"
echo ""
echo "⚠️  請勿關閉此視窗，關閉即停止 Dashboard"
echo "   按 Ctrl+C 可停止伺服器"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 設置退出時清理
cleanup() {
    echo ""
    echo "🛑 正在停止 Dashboard..."
    pkill -P $$ 2>/dev/null
    echo "✅ Dashboard 已停止"
    exit 0
}

trap cleanup EXIT INT TERM

# 自動開啟瀏覽器
sleep 1
open "http://localhost:3737" 2>/dev/null || true

# 啟動 Node.js 伺服器
node backend/server.js

# 伺服器停止後
echo ""
echo "👋 Dashboard 已停止"
echo ""
read -p "按 Enter 鍵關閉視窗..."
