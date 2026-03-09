#!/bin/bash
# ============================================
# 獵頭顧問技能安裝腳本
# 用途：將技能複製到新 Bot 的 workspace
# ============================================

set -e

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🦞 獵頭顧問技能安裝程式"
echo "================================"

# 設定目標目錄（預設為 ~/clawd）
TARGET_DIR="${1:-$HOME/clawd}"

echo -e "${YELLOW}目標目錄: $TARGET_DIR${NC}"

# 建立目錄
echo "📁 建立目錄結構..."
mkdir -p "$TARGET_DIR/skills/headhunter/scripts"
mkdir -p "$TARGET_DIR/skills/headhunter/templates"
mkdir -p "$TARGET_DIR/skills/headhunter/references"
mkdir -p "$TARGET_DIR/skills/headhunter/config"
mkdir -p "$TARGET_DIR/data/headhunter"

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 複製檔案
echo "📋 複製技能檔案..."

# 主要檔案
cp "$SCRIPT_DIR/SKILL.md" "$TARGET_DIR/skills/headhunter/"

# 腳本
cp "$SCRIPT_DIR/scripts/"*.py "$TARGET_DIR/skills/headhunter/scripts/" 2>/dev/null || true
cp "$SCRIPT_DIR/scripts/"*.sh "$TARGET_DIR/skills/headhunter/scripts/" 2>/dev/null || true

# 模板
cp "$SCRIPT_DIR/templates/"* "$TARGET_DIR/skills/headhunter/templates/" 2>/dev/null || true

# 參考資料
cp "$SCRIPT_DIR/references/"* "$TARGET_DIR/skills/headhunter/references/" 2>/dev/null || true

# 設定檔
cp "$SCRIPT_DIR/config/"* "$TARGET_DIR/skills/headhunter/config/" 2>/dev/null || true

# 設定執行權限
chmod +x "$TARGET_DIR/skills/headhunter/scripts/"*.py 2>/dev/null || true
chmod +x "$TARGET_DIR/skills/headhunter/scripts/"*.sh 2>/dev/null || true

# 初始化資料檔案
echo "💾 初始化資料檔案..."
echo "[]" > "$TARGET_DIR/data/headhunter/jobs.json"
echo "[]" > "$TARGET_DIR/data/headhunter/candidates.json"
echo "[]" > "$TARGET_DIR/data/headhunter/followups.json"

echo ""
echo -e "${GREEN}✅ 安裝完成！${NC}"
echo ""
echo "================================"
echo "📂 已安裝到: $TARGET_DIR/skills/headhunter/"
echo ""
echo "📋 接下來請設定："
echo "   1. gog 連結 Email 帳號"
echo "   2. 告知 Bot Telegram 群組 ID 和 Topic ID"
echo "   3. 測試：python3 $TARGET_DIR/skills/headhunter/scripts/dashboard.py"
echo ""
echo "🦞 Happy Recruiting!"
