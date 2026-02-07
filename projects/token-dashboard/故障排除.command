#!/bin/bash

# Dashboard 故障排除腳本
# 自動診斷和修復常見問題

clear

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║        🔧 Dashboard 故障排除工具 🔧                 ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 獲取腳本所在目錄
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "正在診斷問題..."
echo ""

# 問題 1: 檢查端口佔用
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  檢查 3737 端口狀態"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if lsof -i :3737 &> /dev/null; then
    echo "❌ 問題：3737 端口已被佔用"
    echo ""
    echo "佔用情況："
    lsof -i :3737
    echo ""
    
    read -p "是否要清理舊進程？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 正在清理..."
        pkill -f "node.*server.js" 2>/dev/null
        sleep 2
        
        if lsof -i :3737 &> /dev/null; then
            echo "⚠️  無法自動清理，請手動執行："
            echo "   lsof -i :3737"
            echo "   kill -9 <PID>"
        else
            echo "✅ 清理完成"
        fi
    fi
else
    echo "✅ 端口正常，未被佔用"
fi

echo ""

# 問題 2: 檢查 Node.js
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  檢查 Node.js 環境"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node -v)"
    echo "✅ npm: $(npm -v)"
else
    echo "❌ 問題：未安裝 Node.js"
    echo ""
    echo "🔧 解決方案："
    echo "   1. 前往 https://nodejs.org/"
    echo "   2. 下載並安裝 LTS 版本"
    echo "   3. 重新啟動終端機"
fi

echo ""

# 問題 3: 檢查依賴
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  檢查依賴安裝"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "node_modules" ]; then
    echo "✅ node_modules 存在"
    
    # 檢查關鍵依賴
    if [ -d "node_modules/express" ]; then
        echo "✅ express 已安裝"
    else
        echo "❌ 缺少 express"
    fi
    
    if [ -d "node_modules/sqlite3" ]; then
        echo "✅ sqlite3 已安裝"
    else
        echo "❌ 缺少 sqlite3"
    fi
else
    echo "❌ 問題：未安裝依賴"
    echo ""
    
    read -p "是否要立即安裝？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 正在安裝依賴..."
        npm install
        echo "✅ 安裝完成"
    fi
fi

echo ""

# 問題 4: 檢查 OpenClaw
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  檢查 OpenClaw 環境"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v openclaw &> /dev/null; then
    echo "✅ OpenClaw: $(openclaw --version 2>/dev/null || echo '已安裝')"
    
    # 檢查配置文件
    if [ -f "$HOME/.openclaw/openclaw.json" ]; then
        echo "✅ 配置文件存在"
    else
        echo "⚠️  配置文件不存在"
        echo "   首次使用請執行: openclaw configure"
    fi
    
    # 檢查 Gateway（使用快速方法）
    if pgrep -f "openclaw.*gateway" &> /dev/null; then
        echo "✅ Gateway: 運行中"
    else
        echo "⚠️  Gateway: 未運行"
        echo ""
        
        read -p "是否要啟動 Gateway？(y/n) " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔧 正在啟動 Gateway..."
            openclaw gateway start
            sleep 2
            
            if pgrep -f "openclaw.*gateway" &> /dev/null; then
                echo "✅ Gateway 已啟動"
            else
                echo "❌ Gateway 啟動失敗"
                echo "   請手動執行: openclaw gateway start"
            fi
        fi
    fi
else
    echo "⚠️  未安裝 OpenClaw"
    echo "   Dashboard 仍可運行，但部分功能受限"
fi

echo ""

# 問題 5: 檢查資料庫
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  檢查資料庫"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "backend/db/openclaw-tokens.db" ]; then
    DB_SIZE=$(du -h backend/db/openclaw-tokens.db | cut -f1)
    echo "✅ 資料庫存在 (大小: $DB_SIZE)"
else
    echo "⚠️  資料庫不存在"
    echo "   這是正常的（首次使用）"
    echo "   資料庫會在第一次運行時自動創建"
fi

echo ""

# 總結
echo "╔══════════════════════════════════════════════════════╗"
echo "║                    診斷完成                          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "📋 常見問題解決方案："
echo ""
echo "1️⃣  端口被佔用 (EADDRINUSE)"
echo "   → 執行: pkill -f 'node.*server.js'"
echo ""
echo "2️⃣  無法啟動 Dashboard"
echo "   → 確認已安裝依賴: npm install"
echo "   → 確認 Node.js 版本 >= 14"
echo ""
echo "3️⃣  前端無法連接"
echo "   → 確認伺服器正在運行"
echo "   → 瀏覽器刷新: Cmd+Shift+R"
echo ""
echo "4️⃣  模型切換失敗"
echo "   → 確認 Gateway 正在運行"
echo "   → 檢查 ~/.openclaw/openclaw.json"
echo ""
echo "5️⃣  手機無法訪問"
echo "   → 確認同一個 WiFi"
echo "   → 檢查防火牆設定"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "是否要現在啟動 Dashboard？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 正在啟動 Dashboard..."
    echo ""
    ./啟動\ Dashboard.command
else
    echo ""
    echo "👋 稍後您可以雙擊「啟動 Dashboard.command」來啟動"
fi
