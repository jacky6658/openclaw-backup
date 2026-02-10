#!/bin/bash
# JD 管理工具 - 職缺描述管理系統

set -e

# === 設定 ===
ACCOUNT="aiagentg888@gmail.com"
JD_SHEET_ID="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
RESUME_SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"

# 顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# === 函數 ===

# 列出所有職缺
list_jd() {
    echo -e "${BLUE}📋 職缺清單${NC}"
    echo "===================="
    
    DATA=$(gog sheets get "$JD_SHEET_ID" "A1:L100" --account "$ACCOUNT" --plain 2>/dev/null || echo "")
    
    if [ -z "$DATA" ] || [ "$(echo "$DATA" | wc -l)" -eq 1 ]; then
        echo -e "${YELLOW}目前沒有職缺${NC}"
        echo ""
        echo -e "${BLUE}📊 查看完整列表: https://docs.google.com/spreadsheets/d/$JD_SHEET_ID/edit${NC}"
        return
    fi
    
    echo "$DATA" | column -t -s $'\t'
    echo ""
    echo -e "${GREEN}📊 查看完整列表: https://docs.google.com/spreadsheets/d/$JD_SHEET_ID/edit${NC}"
}

# 新增職缺
add_jd() {
    local title="$1"
    local company="$2"
    local dept="$3"
    local count="$4"
    local salary="$5"
    local skills="$6"
    local exp="$7"
    local edu="$8"
    local location="${9:-台北}"
    local status="${10:-開放中}"
    local create_date=$(date +"%Y-%m-%d")
    local update_date="$create_date"
    
    if [ -z "$title" ] || [ -z "$company" ]; then
        echo -e "${RED}❌ 錯誤: 缺少必要欄位${NC}"
        echo "用法: $0 add <職位名稱> <客戶公司> <部門> <需求人數> <薪資範圍> <主要技能> <經驗要求> <學歷要求> [工作地點] [狀態]"
        echo "範例: $0 add 'AI工程師' '美德醫療' '技術部' '2' '80k-120k' 'Python、AI、ML' '3年以上' '大學' '台北' '開放中'"
        return 1
    fi
    
    # 預設值處理
    dept="${dept:-待確認}"
    count="${count:-1}"
    salary="${salary:-面議}"
    skills="${skills:-詳見職缺說明}"
    exp="${exp:-不拘}"
    edu="${edu:-不拘}"
    
    echo -e "${BLUE}📝 新增職缺...${NC}"
    
    # 使用頓號分隔技能（避免逗號被當作分隔符）
    skills_formatted=$(echo "$skills" | sed 's/,/、/g')
    
    # 使用 pipe 分隔欄位（gog sheets 正確格式）
    gog sheets append "$JD_SHEET_ID" "A:L" \
        "${title}|${company}|${dept}|${count}|${salary}|${skills_formatted}|${exp}|${edu}|${location}|${status}|${create_date}|${update_date}" \
        --account "$ACCOUNT" > /dev/null
    
    echo -e "${GREEN}✓ 職缺已新增${NC}"
    echo ""
    echo "職位: $title"
    echo "公司: $company"
    echo "部門: $dept"
    echo "需求: $count 人"
    echo "薪資: $salary"
    echo "技能: $skills_formatted"
    echo "經驗: $exp"
    echo "學歷: $edu"
    echo "地點: $location"
    echo "狀態: $status"
}

# 搜尋職缺
search_jd() {
    local keyword="$1"
    
    if [ -z "$keyword" ]; then
        echo -e "${RED}❌ 請提供搜尋關鍵字${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔍 搜尋職缺: $keyword${NC}"
    echo "===================="
    
    DATA=$(gog sheets get "$JD_SHEET_ID" "A1:L100" --account "$ACCOUNT" --plain 2>/dev/null || echo "")
    
    RESULT=$(echo "$DATA" | grep -i "$keyword" || echo "")
    
    if [ -z "$RESULT" ]; then
        echo -e "${YELLOW}沒有找到相關職缺${NC}"
        return
    fi
    
    echo "$RESULT" | column -t -s $'\t'
}

# 更新職缺狀態
update_status() {
    local row="$1"
    local new_status="$2"
    
    if [ -z "$row" ] || [ -z "$new_status" ]; then
        echo -e "${RED}❌ 錯誤: 缺少必要參數${NC}"
        echo "用法: $0 update-status <行數> <新狀態>"
        echo "狀態選項: 開放中 | 面試中 | 暫停招募 | 已結束"
        return 1
    fi
    
    local update_date=$(date +"%Y-%m-%d %H:%M:%S")
    
    echo -e "${BLUE}📝 更新職缺狀態...${NC}"
    
    gog sheets update "$JD_SHEET_ID" "I${row}" "$new_status" --account "$ACCOUNT" > /dev/null
    gog sheets update "$JD_SHEET_ID" "K${row}" "$update_date" --account "$ACCOUNT" > /dev/null
    
    echo -e "${GREEN}✓ 狀態已更新為: $new_status${NC}"
}

# 產生職缺統計報表
report_jd() {
    echo -e "${BLUE}📊 職缺統計報表${NC}"
    echo "===================="
    
    DATA=$(gog sheets get "$JD_SHEET_ID" "A2:L100" --account "$ACCOUNT" --plain 2>/dev/null || echo "")
    
    if [ -z "$DATA" ]; then
        echo -e "${YELLOW}目前沒有職缺資料${NC}"
        return
    fi
    
    local total=$(echo "$DATA" | wc -l | xargs)
    local open=$(echo "$DATA" | grep -c "開放中" || echo "0")
    local interview=$(echo "$DATA" | grep -c "面試中" || echo "0")
    local paused=$(echo "$DATA" | grep -c "暫停招募" || echo "0")
    local closed=$(echo "$DATA" | grep -c "已結束" || echo "0")
    
    echo "總職缺數: $total"
    echo "開放中: $open"
    echo "面試中: $interview"
    echo "暫停招募: $paused"
    echo "已結束: $closed"
    echo ""
    echo -e "${BLUE}📊 各公司職缺數:${NC}"
    echo "$DATA" | awk -F'\t' '{print $2}' | sort | uniq -c | sort -rn
    echo ""
    echo -e "${BLUE}📊 各部門職缺數:${NC}"
    echo "$DATA" | awk -F'\t' '{print $3}' | sort | uniq -c | sort -rn
    echo ""
    echo -e "${GREEN}📊 查看完整報表: https://docs.google.com/spreadsheets/d/$JD_SHEET_ID/edit${NC}"
}

# 初始化
init_jd() {
    echo -e "${BLUE}🔧 初始化職缺管理系統${NC}"
    
    HEADER=$(gog sheets get "$JD_SHEET_ID" "A1" --account "$ACCOUNT" --plain 2>/dev/null || echo "")
    
    if echo "$HEADER" | grep -q "職位名稱"; then
        echo -e "${GREEN}✓ 表頭已存在${NC}"
    else
        echo -e "${YELLOW}⚠ 建立表頭...${NC}"
        gog sheets update "$JD_SHEET_ID" "A1:L1" \
            "職位名稱|客戶公司|部門|需求人數|薪資範圍|主要技能|經驗要求|學歷要求|工作地點|職位狀態|建立日期|最後更新" \
            --account "$ACCOUNT" > /dev/null
        echo -e "${GREEN}✓ 表頭已建立${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}📊 職缺管理系統已就緒${NC}"
    echo -e "${BLUE}連結: https://docs.google.com/spreadsheets/d/$JD_SHEET_ID/edit${NC}"
}

# 說明
show_help() {
    cat << EOF
📋 JD 管理工具
==================

指令列表:
  init          初始化職缺管理系統
  add           新增職缺
  list          列出所有職缺
  search        搜尋職缺
  update-status 更新職缺狀態
  report        產生統計報表

範例:
  $0 init
  $0 add 'AI工程師' '技術部' '2' '80k-120k' 'Python,AI,ML' '3年以上' '大學' '台北' '開放中'
  $0 list
  $0 search 'AI'
  $0 update-status 2 '面試中'
  $0 report

狀態選項:
  - 開放中
  - 面試中
  - 暫停招募
  - 已結束

Google Sheets:
  - 職缺管理: https://docs.google.com/spreadsheets/d/$JD_SHEET_ID/edit
  - 履歷池: https://docs.google.com/spreadsheets/d/$RESUME_SHEET_ID/edit

EOF
}

# === 主程式 ===

case "${1:-help}" in
    init)
        init_jd
        ;;
    add)
        add_jd "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}"
        ;;
    list)
        list_jd
        ;;
    search)
        search_jd "$2"
        ;;
    update-status)
        update_status "$2" "$3"
        ;;
    report)
        report_jd
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ 未知指令: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
