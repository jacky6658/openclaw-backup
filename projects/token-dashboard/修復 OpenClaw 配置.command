#!/bin/bash

# OpenClaw 配置修復工具
# 自動修復配置檔案並重新安裝 Gateway

clear

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║        🔧 OpenClaw 配置修復工具 🔧                  ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

CONFIG_FILE="$HOME/.openclaw/openclaw.json"
BACKUP_FILE="$HOME/.openclaw/openclaw.json.backup-$(date +%Y%m%d-%H%M%S)"

# 檢查配置檔案
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 找不到配置檔案: $CONFIG_FILE"
    echo ""
    read -p "按 Enter 鍵關閉視窗..."
    exit 1
fi

echo "📍 配置檔案: $CONFIG_FILE"
echo ""

# 診斷問題
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  診斷配置問題"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔍 執行診斷..."
if openclaw doctor 2>&1 | grep -q "Unrecognized key"; then
    echo "❌ 發現配置格式錯誤"
    echo ""
    openclaw doctor 2>&1 | grep "Unrecognized"
    echo ""
    
    HAS_ERROR=true
else
    echo "✅ 配置格式正確"
    HAS_ERROR=false
fi

# 檢查舊的 llm 欄位
if grep -q "\"llm\"" "$CONFIG_FILE"; then
    echo "⚠️  發現舊格式 'llm' 欄位"
    HAS_ERROR=true
fi

echo ""

if [ "$HAS_ERROR" = "false" ]; then
    echo "✅ 配置檔案沒有問題"
    echo ""
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "2️⃣  修復配置檔案"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    read -p "是否要修復配置檔案？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 正在備份..."
        cp "$CONFIG_FILE" "$BACKUP_FILE"
        echo "✅ 已備份到: $BACKUP_FILE"
        echo ""
        
        echo "🔧 正在移除 'llm' 欄位..."
        # 使用 Python 處理 JSON（更安全）
        python3 << 'PYTHON_SCRIPT'
import json
import sys

try:
    with open(sys.argv[1], 'r') as f:
        config = json.load(f)
    
    # 移除 llm 欄位
    if 'llm' in config:
        del config['llm']
        print("✅ 已移除 'llm' 欄位")
    
    # 寫回檔案
    with open(sys.argv[1], 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ 配置檔案已修復")
except Exception as e:
    print(f"❌ 修復失敗: {e}")
    sys.exit(1)
PYTHON_SCRIPT
 "$CONFIG_FILE"
        
        echo ""
        echo "🔍 驗證修復..."
        if openclaw doctor 2>&1 | grep -q "Unrecognized key"; then
            echo "❌ 修復失敗，仍有錯誤"
            echo ""
            echo "請手動編輯配置檔案或重新執行:"
            echo "  openclaw configure"
        else
            echo "✅ 配置檔案已修復成功"
        fi
        echo ""
    else
        echo "⏭️  跳過修復"
        echo ""
    fi
fi

# 檢查 Gateway 服務
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  檢查 Gateway 服務"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if launchctl print gui/$(id -u)/ai.openclaw.gateway &> /dev/null; then
    echo "✅ Gateway 服務已安裝"
    
    # 檢查是否運行
    if pgrep -f "openclaw-gateway" &> /dev/null; then
        echo "✅ Gateway 正在運行"
    else
        echo "⚠️  Gateway 未運行"
        echo ""
        
        read -p "是否要啟動 Gateway？(y/n) " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            openclaw gateway start
            sleep 2
            
            if pgrep -f "openclaw-gateway" &> /dev/null; then
                echo "✅ Gateway 已啟動"
            else
                echo "❌ Gateway 啟動失敗"
                echo "   查看日誌: openclaw logs"
            fi
        fi
    fi
else
    echo "❌ Gateway 服務未安裝"
    echo ""
    
    read -p "是否要安裝 Gateway 服務？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 正在安裝 Gateway..."
        openclaw gateway install
        sleep 2
        
        if launchctl print gui/$(id -u)/ai.openclaw.gateway &> /dev/null; then
            echo "✅ Gateway 服務已安裝"
            echo ""
            
            # 啟動 Gateway
            echo "🚀 正在啟動 Gateway..."
            openclaw gateway start
            sleep 2
            
            if pgrep -f "openclaw-gateway" &> /dev/null; then
                echo "✅ Gateway 已啟動"
            else
                echo "⚠️  Gateway 啟動失敗"
                echo "   查看日誌: openclaw logs"
            fi
        else
            echo "❌ Gateway 服務安裝失敗"
        fi
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  最終驗證"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 檢查配置
if openclaw doctor 2>&1 | grep -q "Unrecognized key"; then
    echo "❌ 配置仍有錯誤"
else
    echo "✅ 配置正確"
fi

# 檢查 Gateway
if pgrep -f "openclaw-gateway" &> /dev/null; then
    GATEWAY_PID=$(pgrep -f "openclaw-gateway" | head -1)
    echo "✅ Gateway 運行中 (PID: $GATEWAY_PID)"
else
    echo "❌ Gateway 未運行"
fi

# 測試 Control UI
if curl -s http://localhost:18789/api/status &> /dev/null; then
    echo "✅ Gateway Control UI 可訪問"
else
    echo "⚠️  Gateway Control UI 無法訪問"
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                    完成！                            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

if pgrep -f "openclaw-gateway" &> /dev/null; then
    echo "✅ 所有問題已修復"
    echo "✅ 現在可以重啟 Dashboard"
    echo ""
    echo "下一步："
    echo "  雙擊「啟動 Dashboard.command」"
else
    echo "⚠️  Gateway 仍未運行"
    echo ""
    echo "建議："
    echo "  1. 執行: openclaw logs"
    echo "  2. 查看錯誤訊息"
    echo "  3. 或執行: openclaw configure 重新配置"
fi

echo ""
echo "📝 備份檔案位置:"
echo "   $BACKUP_FILE"
echo ""
read -p "按 Enter 鍵關閉視窗..."
