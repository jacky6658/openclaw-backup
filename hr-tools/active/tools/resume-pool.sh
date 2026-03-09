#!/bin/bash
# 履歷池管理工具
# 用法: ./resume-pool.sh <command> [args]

ACCOUNT="aiagentg888@gmail.com"
SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"

# 資料夾 ID
PENDING_FOLDER="1M3jX7JbtQtEwtjfj_GG3UPnSRIcmGezu"
INTERVIEWED_FOLDER="1SNK01mbBXB6kTIdTE0UCfiilx6fZQiZK"
HIRED_FOLDER="1m9uUt_S-9Rik3Uzzw0Kqoa-s9VJkm0fk"
REJECTED_FOLDER="1lTuP8RCU4K2bpg-TNODN1xPm4EOru2RN"

command=$1
shift

case "$command" in
  add)
    # 新增履歷: ./resume-pool.sh add "張三" "0912345678" "工程師" "Python,AI" "3" "碩士" "顧問名稱" "/path/to/resume.pdf"
    name=$1
    contact=$2
    position=$3
    skills=$4
    experience=$5
    education=$6
    consultant=$7
    file_path=$8
    
    if [ -z "$file_path" ]; then
      echo "❌ 使用方式: add <姓名> <聯絡方式> <職位> <技能> <經驗年數> <學歷> <獵頭顧問> <檔案路徑>"
      exit 1
    fi
    
    # 上傳履歷到 pending 資料夾
    echo "📤 上傳履歷..."
    upload_result=$(gog drive upload "$file_path" --parent "$PENDING_FOLDER" --account "$ACCOUNT" --json)
    file_id=$(echo "$upload_result" | jq -r '.file.id')
    file_link=$(echo "$upload_result" | jq -r '.file.webViewLink')
    
    if [ -z "$file_id" ] || [ "$file_id" = "null" ]; then
      echo "❌ 上傳失敗"
      exit 1
    fi
    
    # 新增到 Google Sheets
    today=$(date +"%Y-%m-%d")
    echo "📝 新增到索引..."
    gog sheets append "$SHEET_ID" "A:L" \
      --values-json "[
        [\"$name\",\"$contact\",\"$position\",\"$skills\",\"$experience\",\"$education\",\"$file_link\",\"待審核\",\"$consultant\",\"\",\"$today\",\"$today\"]
      ]" \
      --insert INSERT_ROWS \
      --input USER_ENTERED \
      --account "$ACCOUNT" \
      --json
    
    echo "✅ 履歷已新增！檔案 ID: $file_id"
    echo "👔 獵頭顧問: $consultant"
    echo "📊 查看索引: https://docs.google.com/spreadsheets/d/$SHEET_ID"
    ;;
    
  search)
    # 搜尋履歷: ./resume-pool.sh search "Python"
    keyword=$1
    if [ -z "$keyword" ]; then
      echo "❌ 使用方式: search <關鍵字>"
      exit 1
    fi
    
    echo "🔍 搜尋關鍵字: $keyword"
    gog sheets get "$SHEET_ID" "A:K" --account "$ACCOUNT" --json | \
      jq -r --arg kw "$keyword" '.values[] | select(. | tostring | contains($kw)) | @tsv'
    ;;
    
  status)
    # 更新狀態: ./resume-pool.sh status 2 "已面試"
    row=$1
    new_status=$2
    
    if [ -z "$row" ] || [ -z "$new_status" ]; then
      echo "❌ 使用方式: status <行數> <新狀態>"
      echo "狀態選項: 待審核 | 已面試 | 已錄取 | 已拒絕"
      exit 1
    fi
    
    # 取得檔案 ID（從該行的履歷連結）
    file_link=$(gog sheets get "$SHEET_ID" "G$row" --account "$ACCOUNT" --json | jq -r '.values[0][0]')
    file_id=$(echo "$file_link" | grep -oP 'd/\K[^/]+')
    
    # 根據狀態移動檔案
    case "$new_status" in
      "待審核") target_folder="$PENDING_FOLDER" ;;
      "已面試") target_folder="$INTERVIEWED_FOLDER" ;;
      "已錄取") target_folder="$HIRED_FOLDER" ;;
      "已拒絕") target_folder="$REJECTED_FOLDER" ;;
      *) echo "❌ 無效狀態"; exit 1 ;;
    esac
    
    # 移動檔案
    echo "📁 移動履歷檔案..."
    gog drive move "$file_id" --parent "$target_folder" --account "$ACCOUNT" --json
    
    # 更新 Google Sheets（只更新狀態和更新日期）
    today=$(date +"%Y-%m-%d")
    echo "📝 更新索引..."
    gog sheets update "$SHEET_ID" "H$row" \
      --values-json "[[\"$new_status\"]]" \
      --input USER_ENTERED \
      --account "$ACCOUNT" \
      --json
    gog sheets update "$SHEET_ID" "L$row" \
      --values-json "[[\"$today\"]]" \
      --input USER_ENTERED \
      --account "$ACCOUNT" \
      --json
    
    echo "✅ 狀態已更新: $new_status"
    ;;
    
  list)
    # 列出所有履歷
    echo "📋 履歷池列表："
    gog sheets get "$SHEET_ID" "A:L" --account "$ACCOUNT" --json | jq -r '.values[] | @tsv'
    ;;
    
  report)
    # 產生報表
    echo "📊 履歷池統計報表"
    echo "===================="
    
    all_data=$(gog sheets get "$SHEET_ID" "A:L" --account "$ACCOUNT" --json | jq -r '.values[1:]')
    
    total=$(echo "$all_data" | jq 'length')
    pending=$(echo "$all_data" | jq '[.[] | select(.[7] == "待審核")] | length')
    interviewed=$(echo "$all_data" | jq '[.[] | select(.[7] == "已面試")] | length')
    hired=$(echo "$all_data" | jq '[.[] | select(.[7] == "已錄取")] | length')
    rejected=$(echo "$all_data" | jq '[.[] | select(.[7] == "已拒絕")] | length')
    
    echo "總履歷數: $total"
    echo "待審核: $pending"
    echo "已面試: $interviewed"
    echo "已錄取: $hired"
    echo "已拒絕: $rejected"
    echo ""
    echo "📊 查看完整索引: https://docs.google.com/spreadsheets/d/$SHEET_ID"
    ;;
    
  help|*)
    echo "📋 履歷池管理工具"
    echo "=================="
    echo ""
    echo "指令列表:"
    echo "  add       新增履歷"
    echo "  search    搜尋履歷"
    echo "  status    更新狀態"
    echo "  list      列出所有履歷"
    echo "  report    產生統計報表"
    echo ""
    echo "範例:"
    echo "  ./resume-pool.sh add '張三' '0912345678' '工程師' 'Python,AI' '3' '碩士' 'Jacky' '/path/to/resume.pdf'"
    echo "  ./resume-pool.sh search 'Python'"
    echo "  ./resume-pool.sh status 2 '已面試'"
    echo "  ./resume-pool.sh list"
    echo "  ./resume-pool.sh report"
    ;;
esac
