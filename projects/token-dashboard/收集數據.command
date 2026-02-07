#!/bin/bash

# OpenClaw Token Dashboard - 數據收集與更新工具

clear

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║        📊 數據收集與更新工具 📊                     ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 獲取腳本所在目錄
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "📍 當前目錄: $DIR"
echo ""

# 檢查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "❌ 錯誤：未安裝 OpenClaw"
    echo ""
    echo "無法收集數據，請先安裝 OpenClaw"
    echo ""
    read -p "按 Enter 鍵關閉視窗..."
    exit 1
fi

echo "✅ OpenClaw: 已安裝"
echo ""

# 檢查 Gateway
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  檢查 Gateway 狀態"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if pgrep -f "openclaw-gateway" &> /dev/null; then
    echo "✅ Gateway: 運行中"
else
    echo "❌ Gateway: 未運行"
    echo ""
    
    read -p "是否要啟動 Gateway？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 正在啟動 Gateway..."
        openclaw gateway start
        sleep 3
        
        if pgrep -f "openclaw-gateway" &> /dev/null; then
            echo "✅ Gateway 啟動成功"
        else
            echo "❌ Gateway 啟動失敗"
            echo "   數據收集可能不完整"
        fi
    else
        echo "⚠️  繼續收集（但數據可能不完整）"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  開始收集數據"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📊 正在收集 Token 用量數據..."
echo ""

# 執行數據收集
if node backend/collector/collect.js; then
    echo ""
    echo "✅ 數據收集完成"
else
    echo ""
    echo "❌ 數據收集失敗"
    echo "   請檢查錯誤訊息"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  驗證數據"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 檢查資料庫
DB_PATH="backend/db/openclaw-tokens.db"

if [ -f "$DB_PATH" ]; then
    echo "✅ 資料庫存在"
    
    # 查詢資料筆數
    TOKEN_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM token_usage;" 2>/dev/null || echo "0")
    MODEL_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM model_quota;" 2>/dev/null || echo "0")
    
    echo "📊 Token 用量記錄: $TOKEN_COUNT 筆"
    echo "📊 模型配額記錄: $MODEL_COUNT 筆"
    
    if [ "$TOKEN_COUNT" -gt 0 ] || [ "$MODEL_COUNT" -gt 0 ]; then
        echo ""
        echo "✅ 資料庫有數據"
        echo "✅ Dashboard 應該能正常顯示"
    else
        echo ""
        echo "⚠️  資料庫仍然是空的"
        echo ""
        echo "可能原因："
        echo "1. OpenClaw 尚未使用過（沒有歷史數據）"
        echo "2. Gateway 未運行（無法收集即時數據）"
        echo "3. OpenClaw 配置問題"
        echo ""
        echo "建議："
        echo "• 使用 OpenClaw 執行一些查詢"
        echo "• 確保 Gateway 正在運行"
        echo "• 稍後再次執行本工具"
    fi
else
    echo "❌ 資料庫不存在"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  設定自動收集（可選）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CRON_FILE="/tmp/openclaw-collector-cron"

# 檢查是否已設定 cron
if crontab -l 2>/dev/null | grep -q "openclaw.*collect.js"; then
    echo "✅ 已設定自動收集"
    echo "   每 5 分鐘自動執行一次"
    echo ""
    
    read -p "是否要停用自動收集？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        crontab -l 2>/dev/null | grep -v "openclaw.*collect.js" | crontab -
        echo "✅ 已停用自動收集"
    fi
else
    echo "⚠️  未設定自動收集"
    echo "   建議每 5 分鐘收集一次數據"
    echo ""
    
    read -p "是否要啟用自動收集？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 備份現有 crontab
        crontab -l 2>/dev/null > "$CRON_FILE"
        
        # 添加新任務
        echo "*/5 * * * * cd $DIR && node backend/collector/collect.js >> /tmp/openclaw-collector.log 2>&1" >> "$CRON_FILE"
        
        # 安裝新 crontab
        crontab "$CRON_FILE"
        rm "$CRON_FILE"
        
        echo "✅ 已啟用自動收集"
        echo "   每 5 分鐘執行一次"
        echo "   日誌位置: /tmp/openclaw-collector.log"
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                    完成！                            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

if [ "$TOKEN_COUNT" -gt 0 ] || [ "$MODEL_COUNT" -gt 0 ]; then
    echo "✅ 數據收集成功"
    echo "✅ 現在可以重新整理 Dashboard 查看數據"
else
    echo "⚠️  目前無數據"
    echo "   請使用 OpenClaw 後再次收集"
fi

echo ""
echo "💡 提示："
echo "   • 手動收集: 雙擊此檔案"
echo "   • 自動收集: 上方已設定"
echo "   • 查看數據: 開啟 Dashboard"
echo ""
read -p "按 Enter 鍵關閉視窗..."
