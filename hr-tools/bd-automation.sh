#!/bin/bash

# Step1ne BD 客戶開發自動化完整流程
# 觸發：在 Telegram Topic 364「開發」輸入關鍵字

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
CLIENTS_SHEET="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE" # BD客戶開發表
EMAIL_ACCOUNT="aijessie88@step1ne.com"
GOG_ACCOUNT="aiagentg888@gmail.com"

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 建立資料目錄
mkdir -p "$DATA_DIR"

# 說明
show_help() {
    cat << EOF
🤖 Step1ne BD 客戶開發自動化

功能：自動搜尋招聘中的公司，爬取聯絡方式，寄送合作邀請信

用法：
  ./bd-automation.sh search <關鍵字> [數量]    # 搜尋招聘公司
  ./bd-automation.sh scrape <公司列表檔案>    # 爬取公司詳細資料
  ./bd-automation.sh send <公司列表檔案>      # 批量寄信
  ./bd-automation.sh auto <關鍵字> [數量]     # 全自動流程

範例：
  ./bd-automation.sh auto "AI工程師" 20
  # 自動完成：搜尋 → 爬取 → 整理 → 寄信 → 回報

  ./bd-automation.sh search "後端工程師" 10
  ./bd-automation.sh scrape companies.json
  ./bd-automation.sh send companies.json
EOF
}

# 步驟 1：搜尋招聘公司（使用 104）
search_companies() {
    local keyword="$1"
    local limit="${2:-20}"
    
    echo -e "${BLUE}🔍 步驟 1/4：搜尋招聘「${keyword}」的公司...${NC}"
    
    # 使用 scraper-104.py
    local output="$DATA_DIR/companies_$(date +%Y%m%d_%H%M%S).json"
    
    if [[ -f "$SCRIPT_DIR/../skills/headhunter/scripts/scraper-104.py" ]]; then
        python3 "$SCRIPT_DIR/../skills/headhunter/scripts/scraper-104.py" "$keyword" "$limit" > "$output"
    else
        echo -e "${YELLOW}⚠️  找不到 scraper-104.py，使用模擬資料${NC}"
        cat > "$output" << 'EOF'
[
  {
    "company": "ABC科技股份有限公司",
    "job_title": "AI工程師",
    "location": "台北市",
    "salary": "80k-120k",
    "url": "https://www.104.com.tw/job/xxxxx"
  },
  {
    "company": "XYZ資訊有限公司",
    "job_title": "AI工程師",
    "location": "新北市",
    "salary": "70k-110k",
    "url": "https://www.104.com.tw/job/yyyyy"
  }
]
EOF
    fi
    
    local count=$(cat "$output" | jq '. | length' 2>/dev/null || echo "0")
    echo -e "${GREEN}✅ 找到 ${count} 家公司${NC}"
    echo "$output"
}

# 步驟 2：爬取公司詳細資料（電話、Email、網址）
scrape_company_details() {
    local companies_file="$1"
    
    echo -e "${BLUE}🕷️  步驟 2/4：爬取公司詳細資料...${NC}"
    
    # TODO: 實作公司網站爬蟲，提取聯絡方式
    # 目前先用簡化版：Google 搜尋公司名稱 + "聯絡我們"
    
    local output="${companies_file%.json}_detailed.json"
    
    # 簡化版：直接標記為需手動查找
    cat "$companies_file" | jq '[.[] | . + {
        "phone": "待查",
        "email": "待查",
        "website": "待查",
        "contact_person": "您好",
        "status": "待聯繫"
    }]' > "$output"
    
    echo -e "${YELLOW}⚠️  自動爬取功能開發中，目前需手動補充聯絡方式${NC}"
    echo -e "${GREEN}✅ 已生成公司列表：$output${NC}"
    echo "$output"
}

# 步驟 3：整理到 Google Sheets
update_google_sheet() {
    local companies_file="$1"
    
    echo -e "${BLUE}📊 步驟 3/4：整理到 Google Sheets...${NC}"
    
    # 轉換 JSON 為 Sheets 格式
    local rows=$(cat "$companies_file" | jq -r '.[] | [
        .company,
        .phone // "待查",
        .email // "待查",
        .website // "待查",
        .job_title,
        "104",
        .status // "待聯繫",
        (now | strftime("%Y-%m-%d")),
        "待分配",
        (.location // "" | tostring)
    ] | @json' | jq -s '.')
    
    # 取得目前的資料列數
    local last_row=$(gog sheets get "$CLIENTS_SHEET" "工作表1!A:A" --account "$GOG_ACCOUNT" --json 2>/dev/null | jq '.values | length' || echo "1")
    local next_row=$((last_row + 1))
    
    # 寫入 Google Sheets
    echo "$rows" | gog sheets append "$CLIENTS_SHEET" "工作表1!A:J" --values-json - --insert INSERT_ROWS --account "$GOG_ACCOUNT" > /dev/null 2>&1
    
    local count=$(cat "$companies_file" | jq '. | length')
    echo -e "${GREEN}✅ 已寫入 ${count} 筆資料到 Google Sheets${NC}"
    echo -e "${BLUE}📋 查看：https://docs.google.com/spreadsheets/d/$CLIENTS_SHEET${NC}"
}

# 步驟 4：批量寄信
batch_send_emails() {
    local companies_file="$1"
    
    echo -e "${BLUE}📧 步驟 4/4：批量寄送 BD 信...${NC}"
    
    local total=$(cat "$companies_file" | jq '. | length')
    local sent=0
    local skipped=0
    
    # 讀取公司列表
    while IFS= read -r company; do
        local name=$(echo "$company" | jq -r '.company')
        local email=$(echo "$company" | jq -r '.email // "待查"')
        local contact=$(echo "$company" | jq -r '.contact_person // "您好"')
        
        if [[ "$email" != "待查" && "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
            echo -e "${YELLOW}📧 寄信給：$name ($email)${NC}"
            
            # 使用 bd-outreach.sh 寄信
            "$SCRIPT_DIR/bd-outreach.sh" send "$name" "$email" "$contact"
            
            ((sent++))
            sleep 30  # 避免被標記為垃圾信，間隔 30 秒
        else
            echo -e "${RED}⏭️  略過：$name（無有效 Email）${NC}"
            ((skipped++))
        fi
    done < <(cat "$companies_file" | jq -c '.[]')
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ 寄信完成！${NC}"
    echo -e "   已寄送：${sent} 封"
    echo -e "   略過：${skipped} 封（無 Email）"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 生成 Telegram 回報訊息
generate_report() {
    local companies_file="$1"
    local sent="$2"
    local skipped="$3"
    
    local total=$(cat "$companies_file" | jq '. | length')
    
    cat << EOF
✅ BD 客戶開發完成

📊 搜尋結果：
• 找到 ${total} 家公司
• 已寄信：${sent} 家
• 待補充 Email：${skipped} 家

📋 詳細資料：
$(cat "$companies_file" | jq -r '.[] | "• \(.company) - \(.job_title)"' | head -5)
$(if [[ $total -gt 5 ]]; then echo "...還有 $((total - 5)) 家"; fi)

📂 資料檔案：$companies_file
EOF
}

# 全自動流程
auto_flow() {
    local keyword="$1"
    local limit="${2:-20}"
    
    echo -e "${BLUE}🤖 啟動 BD 自動化流程...${NC}"
    echo -e "${BLUE}關鍵字：${keyword}${NC}"
    echo -e "${BLUE}數量：${limit}${NC}"
    echo ""
    
    # 步驟 1：搜尋
    local companies_file
    companies_file=$(search_companies "$keyword" "$limit")
    echo ""
    
    # 步驟 2：爬取
    local detailed_file
    detailed_file=$(scrape_company_details "$companies_file")
    echo ""
    
    # 步驟 3：整理
    update_google_sheet "$detailed_file"
    echo ""
    
    # 步驟 4：寄信
    batch_send_emails "$detailed_file"
    echo ""
    
    # 生成回報
    generate_report "$detailed_file" "$sent" "$skipped"
}

# 主程式
main() {
    case "${1:-}" in
        search)
            search_companies "${2:-AI工程師}" "${3:-20}"
            ;;
        scrape)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ 請指定公司列表檔案${NC}"
                show_help
                exit 1
            fi
            scrape_company_details "$2"
            ;;
        send)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ 請指定公司列表檔案${NC}"
                show_help
                exit 1
            fi
            batch_send_emails "$2"
            ;;
        auto)
            auto_flow "${2:-AI工程師}" "${3:-20}"
            ;;
        *)
            show_help
            ;;
    esac
}

main "$@"
