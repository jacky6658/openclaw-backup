#!/bin/bash

# OpenClaw Token Dashboard - 一鍵打包分享
# 雙擊此檔案自動打包

# 獲取腳本所在目錄
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

clear
echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║        📦 OpenClaw Token Dashboard 打包工具         ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "準備打包專案以分享給朋友..."
echo ""

# 設定輸出位置
OUTPUT_DIR="$HOME/Desktop"
ZIP_NAME="token-dashboard-$(date +%Y%m%d).zip"
OUTPUT_PATH="$OUTPUT_DIR/$ZIP_NAME"

echo "📍 輸出位置：$OUTPUT_PATH"
echo ""
echo "🔧 正在打包..."
echo ""

# 建立排除清單
EXCLUDE_LIST=(
  "node_modules/*"
  ".git/*"
  ".DS_Store"
  "*.log"
  "backend/db/*.db"
  ".env"
)

# 建立 zip 命令參數
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_LIST[@]}"; do
  EXCLUDE_ARGS="$EXCLUDE_ARGS -x \"*/$pattern\""
done

# 切換到父目錄進行打包
cd ..
PROJECT_NAME=$(basename "$DIR")

# 執行打包
eval "zip -r \"$OUTPUT_PATH\" \"$PROJECT_NAME\" $EXCLUDE_ARGS"

# 檢查是否成功
if [ -f "$OUTPUT_PATH" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_PATH" | cut -f1)
    
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                    打包完成！                        ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "✅ 檔案名稱：$ZIP_NAME"
    echo "✅ 檔案大小：$FILE_SIZE"
    echo "✅ 儲存位置：桌面"
    echo ""
    echo "📦 已排除的項目："
    echo "   • node_modules（接收者會自動安裝）"
    echo "   • .git（版本控制）"
    echo "   • *.db（資料庫）"
    echo "   • 日誌檔案"
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                  給朋友的使用說明                     ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "1️⃣  解壓縮 $ZIP_NAME"
    echo ""
    echo "2️⃣  雙擊「啟動 Dashboard.command」"
    echo "    （首次需要：右鍵 > 打開 > 確認）"
    echo ""
    echo "3️⃣  等待自動開啟瀏覽器"
    echo ""
    echo "4️⃣  ✅ 開始使用！"
    echo ""
    echo "📱 想在手機看？"
    echo "   • 雙擊「手機訪問指南.html」"
    echo "   • 點擊「自動偵測我的 IP」"
    echo "   • 掃描 QR Code"
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                    系統需求                          ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "接收者需要先安裝："
    echo "  ✅ Node.js (>= 14.0.0)"
    echo "  ✅ OpenClaw（已配置完成）"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 開啟 Finder 顯示檔案
    open -R "$OUTPUT_PATH"
    
    echo "✨ 已在 Finder 中開啟檔案位置"
    echo ""
else
    echo ""
    echo "❌ 打包失敗"
    echo ""
fi

read -p "按 Enter 鍵關閉視窗..."
