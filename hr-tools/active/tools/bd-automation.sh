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
    
    # 訊息輸出到 stderr，檔案路徑輸出到 stdout
    echo -e "${BLUE}🔍 步驟 1/4：搜尋招聘「${keyword}」的公司...${NC}" >&2
    
    # 使用 scraper-104-v4.py（最新版，已修復反爬蟲問題）
    local output="$DATA_DIR/companies_$(date +%Y%m%d_%H%M%S).json"
    
    if [[ -f "$SCRIPT_DIR/../skills/headhunter/scripts/scraper-104-v4.py" ]]; then
        echo -e "${GREEN}✅ 使用 v4 爬蟲（完整 snapshot 解析，已修復反爬蟲）${NC}" >&2
        python3 "$SCRIPT_DIR/../skills/headhunter/scripts/scraper-104-v4.py" "$keyword" "$limit" > "$output"
    else
        echo -e "${RED}❌ 找不到 scraper-104-v4.py${NC}" >&2
        return 1
    fi
    
    local count=$(cat "$output" | jq '. | length' 2>/dev/null || echo "0")
    echo -e "${GREEN}✅ 找到 ${count} 家公司${NC}" >&2
    echo "$output"  # 只有這行輸出到 stdout
}

# 步驟 2：爬取公司詳細資料（電話、Email、網址）
scrape_company_details() {
    local companies_file="$1"
    
    # 訊息輸出到 stderr
    echo -e "${BLUE}🕷️  步驟 2/4：爬取公司詳細資料...${NC}" >&2
    
    local output="${companies_file%.json}_detailed.json"
    
    # 使用新的爬蟲腳本（自動從 104 + 官網提取聯絡方式）
    if [[ -f "$SCRIPT_DIR/../skills/headhunter/scripts/scraper-company-contact.py" ]]; then
        echo -e "${BLUE}📡 自動爬取聯絡方式（104 + 官網）...${NC}" >&2
        python3 "$SCRIPT_DIR/../skills/headhunter/scripts/scraper-company-contact.py" "$companies_file" > "$output" 2>&1
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ 已完成自動爬取${NC}" >&2
        else
            echo -e "${YELLOW}⚠️  自動爬取失敗，使用預設值${NC}" >&2
            # 降級處理：使用預設值
            cat "$companies_file" | jq '[.[] | . + {
                "phone": "待查",
                "email": "待查",
                "website": "待查",
                "contact_person": "您好",
                "status": "待聯繫"
            }]' > "$output"
        fi
    else
        echo -e "${YELLOW}⚠️  找不到爬蟲腳本，使用預設值${NC}" >&2
        cat "$companies_file" | jq '[.[] | . + {
            "phone": "待查",
            "email": "待查",
            "website": "待查",
            "contact_person": "您好",
            "status": "待聯繫"
        }]' > "$output"
    fi
    
    echo -e "${GREEN}✅ 已生成公司列表：$output${NC}" >&2
    echo "$output"  # 只有這行輸出到 stdout
}

# 步驟 3：整理到 Google Sheets
update_google_sheet() {
    local companies_file="$1"
    
    echo -e "${BLUE}📊 步驟 3/4：整理到 Google Sheets...${NC}"
    
    # 轉換 JSON 為 Sheets 格式（2D 陣列）
    local rows_json=$(cat "$companies_file" | jq '.[] | [
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
    ]' | jq -s '.')
    
    # 寫入 Google Sheets（使用字串參數而非 stdin）
    gog sheets append "$CLIENTS_SHEET" "工作表1!A:J" --values-json "$rows_json" --insert INSERT_ROWS --account "$GOG_ACCOUNT" > /dev/null 2>&1
    
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
    
    # 檢查是否需要步驟 2（v2 爬蟲已包含聯絡方式）
    local detailed_file="$companies_file"
    
    # 檢查是否有 "contact_person" 欄位（v2 爬蟲的標誌）
    local has_contact=$(cat "$companies_file" | jq '.[0] | has("contact_person")' 2>/dev/null || echo "false")
    
    if [[ "$has_contact" == "false" ]]; then
        # v1 爬蟲：需要額外步驟 2
        echo -e "${BLUE}步驟 2：補充聯絡方式...${NC}" >&2
        detailed_file=$(scrape_company_details "$companies_file")
        echo ""
    else
        # v2 爬蟲：已包含聯絡方式
        echo -e "${GREEN}✅ v2 爬蟲已包含聯絡方式，跳過步驟 2${NC}" >&2
        echo ""
    fi
    
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
