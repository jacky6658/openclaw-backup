#!/bin/bash
# 檢查公司研究是否已存在

COMPANY_NAME="$1"

if [ -z "$COMPANY_NAME" ]; then
    echo "用法: $0 <公司名稱>"
    echo "範例: $0 遊戲橘子集團"
    exit 1
fi

COMPANY_FILE="$HOME/clawd/hr-recruitment/companies/${COMPANY_NAME}.md"

if [ -f "$COMPANY_FILE" ]; then
    echo "✅ 公司研究已存在：$COMPANY_FILE"
    echo ""
    echo "📄 檔案資訊："
    ls -lh "$COMPANY_FILE"
    echo ""
    echo "📝 內容預覽："
    head -20 "$COMPANY_FILE"
    echo ""
    echo "---"
    echo "💡 可直接使用此研究，無需重複搜尋"
    exit 0
else
    echo "❌ 公司研究不存在：$COMPANY_FILE"
    echo ""
    echo "📋 需要執行公司背景研究："
    echo "1. 搜尋官網、LinkedIn、104"
    echo "2. 了解產品、服務、文化"
    echo "3. 儲存到 $COMPANY_FILE"
    exit 1
fi
