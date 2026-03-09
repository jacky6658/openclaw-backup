#!/bin/bash
# Step1ne 人才等級自動評級系統 v2
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
echo -e "${BLUE}Step1ne 人才等級自動評級系統 v2${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 計算等級函數
calculate_grade() {
  local stability=$1
  local years=$2
  local education=$3
  local jobChanges=$4
  local lastGap=$5
  
  # 1. 穩定性評分（25%）
  local stability_score=${stability:-0}
  
  # 2. 年資經驗（20%）
  local years_score=0
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
  local changes=${jobChanges:-0}
  if [ "$changes" -eq 0 ]; then
    jobChanges_score=100
  elif [ "$changes" -eq 1 ]; then
    jobChanges_score=90
  elif [ "$changes" -eq 2 ]; then
    jobChanges_score=70
  elif [ "$changes" -eq 3 ]; then
    jobChanges_score=50
  elif [ "$changes" -eq 4 ]; then
    jobChanges_score=30
  else
    jobChanges_score=10
  fi
  
  # 5. 最近gap（5% - 負向指標）
  local gap_score=100
  local gap=${lastGap:-0}
  if [ "$gap" -eq 0 ]; then
    gap_score=100
  elif [ "$gap" -le 3 ]; then
    gap_score=80
  elif [ "$gap" -le 6 ]; then
    gap_score=60
  elif [ "$gap" -le 12 ]; then
    gap_score=40
  else
    gap_score=20
  fi
  
  # 計算加權總分（方案A權重）
  # 技能匹配度（25%）- 暫時使用穩定性代替
  # 穩定性評分（25%）
  # 年資經驗（20%）
  # 學歷背景（15%）
  # 轉職次數（10%）
  # 最近gap（5%）
  
  local total_score=$(echo "scale=2; ($stability_score * 0.25) + ($stability_score * 0.25) + ($years_score * 0.20) + ($education_score * 0.15) + ($jobChanges_score * 0.10) + ($gap_score * 0.05)" | bc)
  
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
  
  echo "${grade}"
}

# 計數器
total=0
updated=0
skipped=0

# 處理候選人（Row 2 開始，最多 300 位）
echo -e "${YELLOW}⏳ 開始批量評級...${NC}"
echo ""

for row in {2..300}; do
  # 讀取必要欄位
  name=$(gog sheets get "$SHEET_ID" "履歷池v2!A${row}" --account "$ACCOUNT" 2>/dev/null | head -1)
  
  # 跳過空行
  if [ -z "$name" ]; then
    break
  fi
  
  ((total++))
  
  # 讀取評分相關欄位
  years=$(gog sheets get "$SHEET_ID" "履歷池v2!F${row}" --account "$ACCOUNT" 2>/dev/null | head -1)
  jobChanges=$(gog sheets get "$SHEET_ID" "履歷池v2!G${row}" --account "$ACCOUNT" 2>/dev/null | head -1)
  lastGap=$(gog sheets get "$SHEET_ID" "履歷池v2!I${row}" --account "$ACCOUNT" 2>/dev/null | head -1)
  education=$(gog sheets get "$SHEET_ID" "履歷池v2!K${row}" --account "$ACCOUNT" 2>/dev/null | head -1)
  stability=$(gog sheets get "$SHEET_ID" "履歷池v2!O${row}" --account "$ACCOUNT" 2>/dev/null | head -1)
  
  # 計算等級
  grade=$(calculate_grade "$stability" "$years" "$education" "$jobChanges" "$lastGap")
  
  # 更新 Google Sheets V 欄
  gog sheets update "$SHEET_ID" "履歷池v2!V${row}" --values-json "[\"$grade\"]" --account "$ACCOUNT" >/dev/null 2>&1
  
  if [ $? -eq 0 ]; then
    ((updated++))
    echo -e "${GREEN}✅ Row ${row}: ${name} → ${grade} 級${NC}"
  else
    ((skipped++))
    echo -e "${RED}❌ Row ${row}: ${name} - 更新失敗${NC}"
  fi
  
  # 每 10 筆顯示進度
  if [ $((updated % 10)) -eq 0 ]; then
    echo -e "${BLUE}   進度: ${updated}/${total}${NC}"
    sleep 2  # 避免 API 限流
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
