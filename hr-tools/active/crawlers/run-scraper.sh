#!/bin/bash
# 穩定爬蟲控制腳本

SCRAPER_DIR="/Users/user/clawd/hr-tools/scraper-stable"
PYTHON="/usr/bin/python3"

case "$1" in
  start)
    echo "🚀 啟動 BD 爬蟲..."
    cd "$SCRAPER_DIR"
    $PYTHON main.py ${2:-302}
    ;;
  
  resume)
    echo "▶️ 繼續爬蟲..."
    cd "$SCRAPER_DIR"
    $PYTHON main.py ${2:-302}
    ;;
  
  status)
    echo "📊 爬蟲狀態："
    if [ -f "$SCRAPER_DIR/progress.json" ]; then
      cat "$SCRAPER_DIR/progress.json" | python3 -m json.tool | grep -E "total_|last_updated"
    else
      echo "尚未開始"
    fi
    ;;
  
  log)
    tail -50 "$SCRAPER_DIR/scraper.log"
    ;;
  
  reset)
    echo "⚠️  重置進度（3秒內按 Ctrl+C 取消）..."
    sleep 3
    rm -f "$SCRAPER_DIR/progress.json"
    echo "✅ 進度已重置"
    ;;
  
  *)
    echo "使用方式:"
    echo "  bash run-scraper.sh start [數量]  # 開始爬蟲"
    echo "  bash run-scraper.sh resume       # 繼續爬蟲"
    echo "  bash run-scraper.sh status       # 查看狀態"
    echo "  bash run-scraper.sh log          # 查看日誌"
    echo "  bash run-scraper.sh reset        # 重置進度"
    ;;
esac
