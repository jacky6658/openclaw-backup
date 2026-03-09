#!/usr/bin/env python3
"""把 Ava 加入 CSV + 生成正確的 JSON 資料"""
import csv
import json

print("🔧 修正：加入 Ava 候選人...")

# 讀取現有 CSV
with open('data/履歷池v2-完成版.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    headers = next(reader)
    rows = list(reader)

print(f"✅ 讀取現有資料：{len(rows)} 筆")

# Ava 的資料（從之前的處理）
ava_work_history = [
    {"company": "Quality Inn & Suites", "title": "客務主管", "duration": "2023/11-2026/2", "years": 2.3},
    {"company": "SRS Windows And Doors", "title": "資料輸入專員", "duration": "2023/3-2023/10", "years": 0.6},
    {"company": "魚可國際文創", "title": "執行長特助", "duration": "2021/12-2022/6", "years": 0.5},
    {"company": "商為水創意", "title": "行政經理", "duration": "2019/9-2022/12", "years": 3.3},
    {"company": "頑石劇團", "title": "行政總監", "duration": "2016/7-2019/7", "years": 3.0}
]

ava_education = {
    "degree": "學士",
    "school": "國立臺中科技大學",
    "major": "休閒事業經營系",
    "year": "2009-2013"
}

# 組成 Ava 的新資料（20欄）
ava_row = [
    "陳宥樺 (Ava Chen)",                           # A: 姓名
    "thisbigsister@gmail.com",                      # B: Email
    "(+1)778-926-4272",                             # C: 電話
    "加拿大安大略省雷灣",                             # D: 地點
    "雙語文件管理師/專案行政專家",                    # E: 職位
    "9.7",                                          # F: 年資
    "5",                                            # G: 轉職次數
    "1.9",                                          # H: 平均任職(月) → 應該是年，先填數字
    "5",                                            # I: gap
    "文件管理 SOP優化 跨部門溝通 政府標案 MS Office Google Workspace CRM系統 英文流利",  # J: 技能
    "國立臺中科技大學 休閒事業經營系 學士",          # K: 學歷
    "Telegram",                                     # L: 來源
    json.dumps(ava_work_history, ensure_ascii=False),  # M: 工作經歷JSON
    "職涯轉換（台灣文創→加拿大服務業）",             # N: 離職原因
    "75",                                           # O: 穩定性
    json.dumps(ava_education, ensure_ascii=False),  # P: 學歷JSON
    "",                                             # Q: DISC
    "已匯入",                                       # R: 狀態
    "Jacky",                                        # S: 顧問
    "2026-02-23 Telegram直接上傳"                  # T: 備註
]

# 加入 Ava
rows.append(ava_row)

print(f"✅ 加入 Ava，總計：{len(rows)} 筆")

# 寫入新 CSV
csv_file = 'data/履歷池v2-完整含Ava.csv'
with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"✅ 已生成：{csv_file}")

# 驗證最後一筆
print(f"\n📋 最後一筆驗證（Ava）：")
print(f"  姓名: {ava_row[0]}")
print(f"  Email: {ava_row[1]}")
print(f"  電話: {ava_row[2]}")
print(f"  地點: {ava_row[3]}")
print(f"  年資: {ava_row[5]} 年")
print(f"  轉職: {ava_row[6]} 次")
print(f"  穩定性: {ava_row[14]} 分")
print(f"  工作經歷JSON: {ava_row[12][:80]}...")
print(f"  學歷JSON: {ava_row[15]}")

print(f"\n✅ 完成！總計 {len(rows)} 筆（227 舊 + 1 Ava）")
