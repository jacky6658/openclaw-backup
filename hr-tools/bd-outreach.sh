#!/bin/bash

# Step1ne BD 客戶開發信自動化工具
# 使用 gog CLI 寄送合作邀請信

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/templates"
CLIENTS_FILE="$SCRIPT_DIR/clients.json"
SENT_LOG="$SCRIPT_DIR/bd-sent.log"
EMAIL_ACCOUNT="aijessie88@step1ne.com"
ATTACHMENT="$SCRIPT_DIR/Step1ne公司簡介.pdf"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 說明
show_help() {
    cat << EOF
📧 Step1ne BD 客戶開發信工具

用法：
  ./bd-outreach.sh send <客戶名稱> <Email> [聯絡人]  # 寄合作邀請信給指定客戶
  ./bd-outreach.sh batch <開始行> <結束行>           # 批量寄信
  ./bd-outreach.sh preview <客戶名稱> [聯絡人]      # 預覽信件內容
  ./bd-outreach.sh list                              # 列出所有客戶

範例：
  ./bd-outreach.sh send "ABC科技" "hr@abc.com" "王經理"
  ./bd-outreach.sh send "XYZ公司" "hr@xyz.com"
  ./bd-outreach.sh preview "ABC科技" "王經理"
  ./bd-outreach.sh batch 1 10

客戶資料：$CLIENTS_FILE
寄信記錄：$SENT_LOG
EOF
}

# 檢查 gog CLI
check_gog() {
    if ! command -v gog &> /dev/null; then
        echo -e "${RED}❌ 找不到 gog CLI${NC}"
        exit 1
    fi
}

# 檢查帳號
check_account() {
    if ! gog auth list | grep -q "$EMAIL_ACCOUNT"; then
        echo -e "${RED}❌ 找不到 $EMAIL_ACCOUNT 帳號${NC}"
        echo "請執行："
        echo "  gog auth add $EMAIL_ACCOUNT --services gmail"
        exit 1
    fi
}

# 載入客戶資料
load_clients() {
    if [[ ! -f "$CLIENTS_FILE" ]]; then
        echo "[]" > "$CLIENTS_FILE"
    fi
    cat "$CLIENTS_FILE"
}

# 生成信件內容（合作邀請信）
generate_email() {
    local client_name="$1"
    local contact_person="${2:-您好}"
    
    local subject="【Step1ne】獵頭合作邀請 - 協助您快速找到優秀人才"
    
    local body
    read -r -d '' body << EOF || true
${contact_person}：

我是 Step1ne 的招募顧問，專注於協助企業快速找到優秀的科技人才。

我們想與 ${client_name} 分享我們的服務如何協助企業提升招募效率：

✅ 我們的優勢：
• AI 驅動的履歷匹配系統 - 精準度達 90% 以上
• 豐富的人才庫 - 涵蓋 AI、後端、前端、數據分析等領域
• 快速交付 - 平均 7 天內推薦合適人選
• 保證期服務 - 90 天內免費替換

📊 近期成功案例：
• 協助某金融科技公司 2 週內找到 3 位資深後端工程師
• 為某 AI 新創公司建立完整的技術團隊（5人）
• 幫助多家企業降低 40% 的招募成本

🎯 如果 ${client_name} 有以下需求，歡迎與我們聯繫：
• 急需特定技能的人才（AI/ML/後端/前端/數據）
• 想建立長期的招募合作關係
• 希望了解市場薪資與人才趨勢

期待與您進一步交流，協助 ${client_name} 找到最合適的人才！

---
Step1ne 招募顧問團隊
📧 Email: aijessie88@step1ne.com
🌐 Website: step1ne.com
EOF

    echo "$subject"
    echo "$body"
}

# 寄送信件
send_email() {
    local client_name="$1"
    local email="$2"
    local contact_person="${3:-您好}"
    
    echo -e "${YELLOW}📧 準備寄信給 ${client_name} (${email})...${NC}"
    
    # 生成信件
    local email_content
    email_content=$(generate_email "$client_name" "$contact_person")
    local subject=$(echo "$email_content" | head -1)
    local body=$(echo "$email_content" | tail -n +2)
    
    # 寄信（附上公司簡介）
    if [[ -f "$ATTACHMENT" ]]; then
        echo "$body" | gog gmail send \
            --to "$email" \
            --subject "$subject" \
            --body-file - \
            --attach "$ATTACHMENT" \
            --account "$EMAIL_ACCOUNT"
        echo -e "${GREEN}📎 已附上公司簡介${NC}"
    else
        echo "$body" | gog gmail send \
            --to "$email" \
            --subject "$subject" \
            --body-file - \
            --account "$EMAIL_ACCOUNT"
        echo -e "${YELLOW}⚠️  找不到公司簡介檔案${NC}"
    fi
    
    # 記錄
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $client_name | $email | $subject" >> "$SENT_LOG"
    
    echo -e "${GREEN}✅ 已寄送給 ${client_name}${NC}"
}

# 預覽信件
preview_email() {
    local client_name="$1"
    local contact_person="${2:-您好}"
    
    local email_content
    email_content=$(generate_email "$client_name" "$contact_person")
    local subject=$(echo "$email_content" | head -1)
    local body=$(echo "$email_content" | tail -n +2)
    
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}主旨：${NC}$subject"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "$body"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 主程式
main() {
    check_gog
    check_account
    
    case "${1:-}" in
        send)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ 請指定客戶名稱${NC}"
                show_help
                exit 1
            fi
            # 這裡需要從 clients.json 讀取客戶資料
            # 簡化版：直接傳參數
            send_email "$2" "${3:-}" "${4:-您好}"
            ;;
        preview)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ 請指定客戶名稱${NC}"
                show_help
                exit 1
            fi
            preview_email "$2" "${3:-您好}"
            ;;
        batch)
            echo -e "${YELLOW}批量寄信功能開發中...${NC}"
            ;;
        list)
            echo -e "${YELLOW}客戶列表：${NC}"
            cat "$CLIENTS_FILE" | jq -r '.[] | "\(.name) (\(.email)) - \(.industry)"' 2>/dev/null || echo "客戶資料為空"
            ;;
        add)
            echo -e "${YELLOW}新增客戶功能開發中...${NC}"
            ;;
        *)
            show_help
            ;;
    esac
}

main "$@"
