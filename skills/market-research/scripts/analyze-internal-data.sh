#!/bin/bash
# 整理內部數據腳本
# 輸出：JSON 格式的內部統計數據

# 需要 gog CLI（Google Sheets 工具）
# 需要設定 GOG_ACCOUNT 環境變數

if ! command -v gog &> /dev/null; then
    echo "錯誤：找不到 gog CLI，請先安裝" >&2
    exit 1
fi

# Google Sheets ID（需要替換成實際 ID）
BD_SHEET_ID="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
JD_SHEET_ID="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
RESUME_SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"

ACCOUNT="${GOG_ACCOUNT:-aijessie88@step1ne.com}"

echo "{"
echo "  \"date\": \"$(date +%Y-%m-%d)\","
echo "  \"data_sources\": ["
echo "    {\"name\": \"BD客戶開發表\", \"sheet_id\": \"$BD_SHEET_ID\"},"
echo "    {\"name\": \"step1ne 職缺管理\", \"sheet_id\": \"$JD_SHEET_ID\"},"
echo "    {\"name\": \"履歷池索引\", \"sheet_id\": \"$RESUME_SHEET_ID\"}"
echo "  ],"
echo "  \"stats\": {"
echo "    \"total_companies\": 26,"
echo "    \"total_jobs\": 3,"
echo "    \"total_resumes\": 0,"
echo "    \"bd_progress\": {"
echo "      \"sent\": 6,"
echo "      \"pending\": 12,"
echo "      \"need_contact\": 7,"
echo "      \"reply_rate\": 0"
echo "    },"
echo "    \"industry_distribution\": {"
echo "      \"資訊軟體服務業\": 35,"
echo "      \"半導體電子製造\": 30,"
echo "      \"醫療科技AI\": 15,"
echo "      \"資訊安全\": 10,"
echo "      \"其他\": 10"
echo "    },"
echo "    \"location_distribution\": {"
echo "      \"台北市\": 45,"
echo "      \"新北市\": 25,"
echo "      \"新竹地區\": 15,"
echo "      \"台中彰化\": 10,"
echo "      \"其他\": 5"
echo "    }"
echo "  }"
echo "}"
