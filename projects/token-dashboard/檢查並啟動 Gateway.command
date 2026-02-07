#!/bin/bash

# OpenClaw Gateway 檢查與啟動工具

clear

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║        🔧 Gateway 檢查與啟動工具 🔧                 ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 檢查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "❌ 錯誤：未安裝 OpenClaw"
    echo ""
    echo "請先安裝 OpenClaw 才能使用 Gateway 功能"
    echo ""
    read -p "按 Enter 鍵關閉視窗..."
    exit 1
fi

echo "✅ OpenClaw: $(openclaw --version 2>/dev/null || echo '已安裝')"
echo ""

# 檢查 Gateway 狀態
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  檢查 Gateway 狀態"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if pgrep -f "openclaw-gateway" &> /dev/null; then
    GATEWAY_PID=$(pgrep -f "openclaw-gateway" | head -1)
    echo "✅ Gateway 正在運行"
    echo "   PID: $GATEWAY_PID"
    echo ""
    
    read -p "是否要重啟 Gateway？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔄 正在重啟 Gateway..."
        openclaw gateway stop
        sleep 2
        openclaw gateway start
        sleep 2
        
        if pgrep -f "openclaw-gateway" &> /dev/null; then
            echo "✅ Gateway 重啟成功"
        else
            echo "❌ Gateway 重啟失敗"
        fi
    fi
else
    echo "❌ Gateway 未運行"
    echo ""
    
    read -p "是否要啟動 Gateway？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🚀 正在啟動 Gateway..."
        openclaw gateway start
        sleep 2
        
        if pgrep -f "openclaw-gateway" &> /dev/null; then
            GATEWAY_PID=$(pgrep -f "openclaw-gateway" | head -1)
            echo "✅ Gateway 啟動成功"
            echo "   PID: $GATEWAY_PID"
        else
            echo "❌ Gateway 啟動失敗"
            echo ""
            echo "可能的原因："
            echo "• OpenClaw 配置不完整"
            echo "• 端口被佔用"
            echo "• 權限問題"
            echo ""
            echo "請嘗試："
            echo "1. 執行: openclaw configure"
            echo "2. 檢查: ~/.openclaw/openclaw.json"
            echo "3. 查看日誌: openclaw logs"
        fi
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Gateway 資訊"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if pgrep -f "openclaw-gateway" &> /dev/null; then
    echo "📊 Gateway 狀態："
    echo ""
    
    # 檢查端口
    if lsof -i :18789 &> /dev/null; then
        echo "✅ Control UI: http://localhost:18789"
    else
        echo "⚠️  Control UI: 未偵測到（可能未啟用）"
    fi
    
    # 檢查 WebSocket
    if lsof -i :18788 &> /dev/null; then
        echo "✅ WebSocket: 運行中"
    else
        echo "⚠️  WebSocket: 未偵測到"
    fi
    
    echo ""
    echo "📝 快速命令："
    echo "   • 查看狀態: openclaw status"
    echo "   • 查看日誌: openclaw logs"
    echo "   • 停止服務: openclaw gateway stop"
    echo "   • 重啟服務: openclaw gateway restart"
else
    echo "❌ Gateway 未運行"
    echo ""
    echo "Dashboard 功能受限："
    echo "   • ❌ 無法切換模型"
    echo "   • ❌ 無法查看即時配額"
    echo "   • ✅ 可查看歷史數據"
    echo "   • ✅ 可查看統計圖表"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  開機自動啟動 (可選)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 檢查是否已安裝為系統服務
if [ -f ~/Library/LaunchAgents/com.openclaw.gateway.plist ]; then
    echo "✅ Gateway 已設定為開機自動啟動"
    echo ""
    
    read -p "是否要停用開機自動啟動？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        launchctl unload ~/Library/LaunchAgents/com.openclaw.gateway.plist 2>/dev/null
        rm ~/Library/LaunchAgents/com.openclaw.gateway.plist
        echo "✅ 已停用開機自動啟動"
    fi
else
    echo "⚠️  Gateway 未設定開機自動啟動"
    echo ""
    
    read -p "是否要啟用開機自動啟動？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔧 正在設定..."
        openclaw gateway install
        echo "✅ 已啟用開機自動啟動"
        echo ""
        echo "提示："
        echo "• 下次開機會自動啟動 Gateway"
        echo "• 可隨時使用本工具停用"
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                    完成！                            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

if pgrep -f "openclaw-gateway" &> /dev/null; then
    echo "✅ Gateway 正在運行"
    echo "✅ Dashboard 所有功能可用"
else
    echo "⚠️  Gateway 未運行"
    echo "⚠️  Dashboard 部分功能受限"
fi

echo ""
read -p "按 Enter 鍵關閉視窗..."
