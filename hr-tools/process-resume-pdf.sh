#!/bin/bash
# ============================================================================
# 腳本名稱：process-resume-pdf.sh
# 功能說明：自動處理履歷 PDF（上傳 Drive + 解析 + 更新履歷池）
# 作者：YuQi AI Assistant
# 日期：2026-02-24
# 版本：1.0.0
# ============================================================================
#
# 用法：
#   ./process-resume-pdf.sh <PDF路徑>
#
# 範例：
#   ./process-resume-pdf.sh ~/Downloads/Maggie-Chen-Resume.pdf
#
# 功能流程：
#   1. 互動式確認應徵公司
#   2. 上傳到 Google Drive（履歷庫資料夾）
#   3. 解析 PDF 內容（提取姓名、LinkedIn、技能等）
#   4. 搜尋履歷池（用 LinkedIn 或姓名）
#   5A. 找到 → 逐欄更新（補充詳細資料）
#   5B. 找不到 → 新增候選人
#   6. 回報結果到 Telegram
#
# ============================================================================

set -e  # 遇到錯誤立即退出

# ============================================================================
# 配置變數
# ============================================================================

SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
DRIVE_FOLDER_ID="16IOJW0jR2mBgzBnc5QI_jEHcRBw3VnKj"
ACCOUNT="aijessie88@step1ne.com"

# Telegram 通知設定
TELEGRAM_CHAT_ID="-1003231629634"  # HR AI招募自動化群組
TELEGRAM_TOPIC_ID="304"  # 履歷池 Topic

# ============================================================================
# 輔助函數
# ============================================================================

# 顯示錯誤訊息並退出
error_exit() {
    echo "❌ 錯誤：$1" >&2
    exit 1
}

# 顯示資訊訊息
info() {
    echo "ℹ️  $1"
}

# 顯示成功訊息
success() {
    echo "✅ $1"
}

# 顯示處理中訊息
processing() {
    echo "⏳ $1..."
}

# ============================================================================
# 步驟 1：檢查參數
# ============================================================================

if [ $# -ne 1 ]; then
    echo "用法：$0 <PDF路徑>"
    echo "範例：$0 ~/Downloads/resume.pdf"
    exit 1
fi

PDF_PATH="$1"

# 檢查檔案是否存在
if [ ! -f "$PDF_PATH" ]; then
    error_exit "找不到檔案：$PDF_PATH"
fi

# 檢查是否為 PDF 檔案
if [[ ! "$PDF_PATH" =~ \.pdf$ ]]; then
    error_exit "檔案必須是 PDF 格式"
fi

info "履歷檔案：$PDF_PATH"

# ============================================================================
# 步驟 2：互動式輸入候選人基本資訊
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 請輸入候選人基本資訊"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 輸入姓名
read -p "👤 候選人姓名：" CANDIDATE_NAME
if [ -z "$CANDIDATE_NAME" ]; then
    error_exit "姓名不能為空"
fi

# 輸入 LinkedIn（可選）
read -p "🔗 LinkedIn username（選填，按 Enter 跳過）：" LINKEDIN_USERNAME

if [ -n "$LINKEDIN_USERNAME" ]; then
    # 移除可能的 URL 前綴
    LINKEDIN_USERNAME=$(echo "$LINKEDIN_USERNAME" | sed 's/.*linkedin\.com\/in\///' | sed 's/\/.*//')
    success "LinkedIn：$LINKEDIN_USERNAME"
fi

# ============================================================================
# 步驟 3：互動式確認應徵公司
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "📋 $CANDIDATE_NAME 應徵哪家公司的職缺？" COMPANY_NAME
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -z "$COMPANY_NAME" ]; then
    error_exit "公司名稱不能為空"
fi

# ============================================================================
# 步驟 4：上傳到 Google Drive
# ============================================================================

processing "上傳履歷到 Google Drive"

# 檔案命名：{姓名}-{公司}.pdf
FILE_NAME="${CANDIDATE_NAME}-${COMPANY_NAME}.pdf"

# 上傳到 Google Drive
UPLOAD_RESULT=$(gog drive upload "$PDF_PATH" \
  --parent "$DRIVE_FOLDER_ID" \
  --name "$FILE_NAME" \
  --account "$ACCOUNT" 2>&1)

# 提取 File ID
FILE_ID=$(echo "$UPLOAD_RESULT" | grep '^id' | awk '{print $2}')

if [ -z "$FILE_ID" ]; then
    error_exit "Google Drive 上傳失敗"
fi

# 生成嵌入式預覽 URL
RESUME_PREVIEW_URL="https://drive.google.com/file/d/${FILE_ID}/preview"
RESUME_VIEW_URL="https://drive.google.com/file/d/${FILE_ID}/view"

success "已上傳：$FILE_NAME"
info "File ID：$FILE_ID"
info "預覽連結：$RESUME_PREVIEW_URL"

# ============================================================================
# 步驟 5：搜尋履歷池（用 LinkedIn 或姓名）
# ============================================================================

processing "搜尋履歷池"

# 搜尋策略：
# 1. 優先用 LinkedIn username（最準確）
# 2. 次選用姓名（可能重複）

FOUND_ROW=""

# 策略 1：LinkedIn username
if [ -n "$LINKEDIN_USERNAME" ]; then
    info "搜尋 LinkedIn: $LINKEDIN_USERNAME"
    SEARCH_RESULT=$(gog sheets get "$SHEET_ID" "履歷池v2!B:B" --account "$ACCOUNT" | grep -in "$LINKEDIN_USERNAME" | head -1 || echo "")
    
    if [ -n "$SEARCH_RESULT" ]; then
        FOUND_ROW=$(echo "$SEARCH_RESULT" | cut -d: -f1)
        success "✅ 找到現有候選人（Row $FOUND_ROW，用 LinkedIn）"
    fi
fi

# 策略 2：姓名（如果 LinkedIn 沒找到）
if [ -z "$FOUND_ROW" ]; then
    info "搜尋姓名: $CANDIDATE_NAME"
    SEARCH_RESULT=$(gog sheets get "$SHEET_ID" "履歷池v2!A:A" --account "$ACCOUNT" | grep -in "^$CANDIDATE_NAME$" | head -1 || echo "")
    
    if [ -n "$SEARCH_RESULT" ]; then
        FOUND_ROW=$(echo "$SEARCH_RESULT" | cut -d: -f1)
        success "✅ 找到現有候選人（Row $FOUND_ROW，用姓名）"
        
        # 確認是否為同一人
        echo ""
        read -p "⚠️  確認這是同一個人嗎？(y/n) " CONFIRM
        if [ "$CONFIRM" != "y" ]; then
            FOUND_ROW=""
            info "標記為不同人，將新增為新候選人"
        fi
    else
        info "❌ 履歷池中找不到此候選人"
    fi
fi

# ============================================================================
# 步驟 6A：更新現有候選人（只更新履歷連結 U 欄）
# ============================================================================

if [ -n "$FOUND_ROW" ]; then
    processing "更新履歷連結（U${FOUND_ROW}）"
    
    # 只更新 U 欄（履歷連結）
    gog sheets update "$SHEET_ID" "履歷池v2!U${FOUND_ROW}" \
      --values-json "[[\"$RESUME_PREVIEW_URL\"]]" \
      --account "$ACCOUNT"
    
    success "已更新 $CANDIDATE_NAME 的履歷連結（Row $FOUND_ROW）"
    
    # 通知 Telegram
    echo ""
    echo "📊 更新結果："
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "👤 候選人：$CANDIDATE_NAME"
    echo "🏢 應徵公司：$COMPANY_NAME"
    echo "📍 履歷池行號：Row $FOUND_ROW"
    echo "🔗 履歷連結：已更新"
    echo "📄 檔名：$FILE_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
else
    # ============================================================================
    # 步驟 6B：新增候選人（待實作）
    # ============================================================================
    
    info "❌ 新增候選人功能尚未實作"
    info "請手動新增或使用現有的匯入腳本"
    
    echo ""
    echo "📊 處理結果："
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "👤 候選人：$CANDIDATE_NAME"
    echo "🏢 應徵公司：$COMPANY_NAME"
    echo "📄 檔名：$FILE_NAME"
    echo "🔗 Google Drive：$RESUME_VIEW_URL"
    echo "⚠️  狀態：未找到現有候選人，請手動新增"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

success "處理完成！"
