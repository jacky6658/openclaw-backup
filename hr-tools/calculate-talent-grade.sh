#!/bin/bash
# Step1ne 人才等級自動評級系統
# 使用方案A權重計算綜合評分並轉換成等級（S/A/B/C/D/F）

set -e

SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT="aijessie88@step1ne.com"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Step1ne 人才等級自動評級系統${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 計算單一候選人等級
calculate_grade() {
  local row=$1
  local name=$2
  local stability=$3
  local years=$4
  local education=$5
  local jobChanges=$6
  local lastGap=$7
  
  # 1. 穩定性評分（25%）
  local stability_score=0
  if [[ "$stability" =~ ^[0-9]+$ ]]; then
    stability_score=$stability
  fi
  
  # 2. 年資經驗（20%）
  local years_score=0
  if [[ "$years" =~ ^[0-9]+$ ]]; then
    if [ "$years" -ge 10 ]; then
      years_score=100
    elif [ "$years" -ge 7 ]; then
      years_score=85
    elif [ "$years" -ge 5 ]; then
      years_score=70
    elif [ "$years" -ge 3 ]; then
      years_score=55
    elif [ "$years" -ge 1 ]; then
      years_score=40
    else
      years_score=20
    fi
  fi
  
  # 3. 學歷背景（15%）
  local education_score=50
  case "$education" in
    *博士*|*PhD*|*Doctor*)
      education_score=100
      ;;
    *碩士*|*Master*|*研究所*)
      education_score=85
      ;;
    *學士*|*大學*|*Bachelor*)
      education_score=70
      ;;
    *專科*|*大專*)
      education_score=55
      ;;
    *高中*|*高職*)
      education_score=40
      ;;
  esac
  
  # 4. 轉職次數（10% - 負向指標）
  local jobChanges_score=100
  if [[ "$jobChanges" =~ ^[0-9]+$ ]]; then
    if [ "$jobChanges" -eq 0 ]; then
      jobChanges_score=100
    elif [ "$jobChanges" -eq 1 ]; then
      jobChanges_score=90
    elif [ "$jobChanges" -eq 2 ]; then
      jobChanges_score=70
    elif [ "$jobChanges" -eq 3 ]; then
      jobChanges_score=50
    elif [ "$jobChanges" -eq 4 ]; then
      jobChanges_score=30
    else
      jobChanges_score=10
    fi
  fi
  
  # 5. 最近gap（5% - 負向指標）
  local gap_score=100
  if [[ "$lastGap" =~ ^[0-9]+$ ]]; then
    if [ "$lastGap" -eq 0 ]; then
      gap_score=100
    elif [ "$lastGap" -le 3 ]; then
      gap_score=80
    elif [ "$lastGap" -le 6 ]; then
      gap_score=60
    elif [ "$lastGap" -le 12 ]; then
      gap_score=40
    else
      gap_score=20
    fi
  fi
  
  # 計算加權總分（方案A權重）
  # 技能匹配度（25%）- 暫時使用穩定性代替
  # 穩定性評分（25%）
  # 年資經驗（20%）
  # 學歷背景（15%）
  # 轉職次數（10%）
  # 最近gap（5%）
  
  local total_score=0
  total_score=$(echo "scale=2; ($stability_score * 0.25) + ($stability_score * 0.25) + ($years_score * 0.20) + ($education_score * 0.15) + ($jobChanges_score * 0.10) + ($gap_score * 0.05)" | bc)
  
  # 四捨五入到整數
  total_score=$(printf "%.0f" "$total_score")
  
  # 轉換成等級
  local grade=""
  if [ "$total_score" -ge 90 ]; then
    grade="S"
  elif [ "$total_score" -ge 80 ]; then
    grade="A"
  elif [ "$total_score" -ge 70 ]; then
    grade="B"
  elif [ "$total_score" -ge 60 ]; then
    grade="C"
  elif [ "$total_score" -ge 50 ]; then
    grade="D"
  else
    grade="F"
  fi
  
  echo "${grade}|${total_score}|${name}"
}

# 讀取所有候選人資料
echo -e "${YELLOW}⏳ 讀取候選人資料...${NC}"

# 取得資料範圍（A2:U500，包含前 500 位候選人）
DATA=$(gog sheets get "$SHEET_ID" "履歷池v2!A2:U500" --account "$ACCOUNT" 2>/dev/null || echo "")

if [ -z "$DATA" ]; then
  echo -e "${RED}❌ 無法讀取候選人資料${NC}"
  exit 1
fi

# 計數器
total=0
updated=0
skipped=0

# 處理每一行
IFS=$'\n'
row_num=2
for line in $DATA; do
  # 解析欄位（用 tab 分隔）
  IFS=$'\t' read -r name email phone location position years jobChanges avgTenure lastGap skills education source workHistory leaveReason stability educationJson personality status consultant notes resumeLink <<< "$line"
  
  # 跳過空行
  if [ -z "$name" ]; then
    ((row_num++))
    continue
  fi
  
  ((total++))
  
  # 計算等級
  result=$(calculate_grade "$row_num" "$name" "$stability" "$years" "$education" "$jobChanges" "$lastGap")
  
  grade=$(echo "$result" | cut -d'|' -f1)
  score=$(echo "$result" | cut -d'|' -f2)
  
  # 更新 Google Sheets V 欄
  gog sheets update "$SHEET_ID" "履歷池v2!V${row_num}" --values-json "[\"$grade\"]" --account "$ACCOUNT" >/dev/null 2>&1
  
  if [ $? -eq 0 ]; then
    ((updated++))
    echo -e "${GREEN}✅ Row ${row_num}: ${name} → ${grade} 級 (${score} 分)${NC}"
  else
    ((skipped++))
    echo -e "${RED}❌ Row ${row_num}: ${name} - 更新失敗${NC}"
  fi
  
  ((row_num++))
  
  # 每 10 筆暫停 1 秒（避免 API 限流）
  if [ $((updated % 10)) -eq 0 ]; then
    sleep 1
  fi
done

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}評級完成${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✅ 總候選人數: ${total}${NC}"
echo -e "${GREEN}✅ 成功更新: ${updated}${NC}"
echo -e "${RED}❌ 失敗: ${skipped}${NC}"
echo ""
