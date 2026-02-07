#!/bin/bash

# OpenClaw Token Dashboard - Electron 快速設置腳本
# 自動安裝 Electron 並設置打包環境

set -e

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║    ⚡ Electron 桌面應用自動設置工具 ⚡              ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 獲取腳本所在目錄
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "📍 當前目錄: $DIR"
echo ""

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 錯誤：未安裝 Node.js"
    echo "   請先安裝: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js: $(node -v)"
echo "✅ npm: $(npm -v)"
echo ""

# 安裝 Electron 相關套件
echo "📦 正在安裝 Electron 及相關套件..."
echo ""

npm install --save-dev electron@latest electron-builder@latest

echo ""
echo "📦 正在安裝應用依賴..."
echo ""

npm install electron-store@latest

echo ""
echo "✅ 套件安裝完成！"
echo ""

# 創建必要的目錄
echo "📁 創建資源目錄..."
mkdir -p assets
echo "✅ 目錄創建完成"
echo ""

# 檢查是否已有 electron-main.js
if [ ! -f "electron-main.js" ]; then
    echo "⚠️  尚未創建 electron-main.js"
    echo "   請執行: node 創建-Electron-主程式.js"
    echo ""
fi

# 檢查圖示
if [ ! -f "assets/icon.png" ]; then
    echo "⚠️  尚未準備圖示檔案"
    echo "   請在 assets/ 目錄下放置："
    echo "   • icon.png (1024x1024)"
    echo "   • icon.icns (macOS)"
    echo "   • icon.ico (Windows)"
    echo ""
fi

echo "╔══════════════════════════════════════════════════════╗"
echo "║                    安裝完成！                        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "📋 下一步："
echo ""
echo "1️⃣  創建 Electron 主程式"
echo "   node 創建-Electron-主程式.js"
echo ""
echo "2️⃣  準備圖示檔案"
echo "   將圖示放入 assets/ 目錄"
echo ""
echo "3️⃣  測試 Electron 應用"
echo "   npm start"
echo ""
echo "4️⃣  打包應用"
echo "   npm run build:mac    # macOS"
echo "   npm run build:win    # Windows"
echo "   npm run build:all    # 全平台"
echo ""
echo "📚 詳細說明: 打包安裝方案.md"
echo ""
