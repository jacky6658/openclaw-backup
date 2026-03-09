# 🚀 Pipeline 追蹤系統 - 完整設計方案

**版本**：v1.0  
**日期**：2026-03-05  
**目的**：自動追蹤候選人招聘進度、監控 SLA、生成每日報告

---

## 📊 一、系統架構

### 數據流

```
每日 08:00 觸發
    ↓
掃描所有候選人
    ├─ 取得 GET /api/candidates?limit=1000
    ├─ 解析每位候選人的 status + progressTracking
    └─ 計算停留天數
    ↓
SLA 監控邏輯
    ├─ 未開始 → 2 天逾期？ ⚠️ 
    ├─ 已聯繫 → 3 天逾期？ ⚠️
    ├─ 已面試 → 7 天逾期？ ⚠️
    └─ Offer → 5 天逾期？ ⚠️
    ↓
生成報告
    ├─ 每日匯報（推送龍蝦社群）
    ├─ SLA 逾期警告（Telegram）
    └─ 進度統計（Kanban 看板數據）
    ↓
存儲狀態
    └─ memory/pipeline-state.json
```

---

## 🎯 二、SLA 定義

### 各狀態 SLA 閾值

```javascript
const SLA_CONFIG = {
  "未開始": {
    threshold_days: 2,          // 新增後 2 天內必須開始評分
    warning_days: 1,            // 提前 1 天警告
    warning_message: "⚠️ 候選人 {name} 新增已 1 天，尚未評分",
    action: "評分"
  },
  
  "已聯繫": {
    threshold_days: 3,          // 聯繫後 3 天內必須回應 / 進展
    warning_days: 2,            // 提前 2 天警告
    warning_message: "⚠️ 候選人 {name} 已聯繫 2 天，尚無回應",
    action: "主動追蹤"
  },
  
  "已面試": {
    threshold_days: 7,          // 面試後 7 天內必須決策
    warning_days: 5,            // 提前 5 天警告
    warning_message: "⚠️ 候選人 {name} 已面試 5 天，尚未決策",
    action: "跟進結果"
  },
  
  "Offer": {
    threshold_days: 5,          // Offer 發出後 5 天內必須簽署
    warning_days: 3,            // 提前 3 天警告
    warning_message: "⚠️ 候選人 {name} Offer 已發 3 天，尚未簽署",
    action: "確認簽署"
  },
  
  "已上職": {
    threshold_days: 0,          // 完成狀態，無 SLA
    is_terminal: true
  },
  
  "婉拒": {
    threshold_days: 0,          // 完成狀態，無 SLA
    is_terminal: true
  }
};
```

---

## 🔍 三、每日掃描邏輯

### 步驟 1：取得所有候選人

```bash
GET /api/candidates?limit=1000

回應結構：
{
  "success": true,
  "count": 1234,
  "data": [
    {
      "id": 123,
      "name": "王小明",
      "status": "已聯繫",
      "createdAt": "2026-03-03T10:30:00Z",
      "updatedAt": "2026-03-04T15:20:00Z",
      "progressTracking": [
        {
          "date": "2026-03-03",
          "event": "未開始",
          "by": "system"
        },
        {
          "date": "2026-03-04",
          "event": "已聯繫",
          "by": "Jacky"
        }
      ]
    }
  ]
}
```

### 步驟 2：計算停留天數

```javascript
function calculateStayDays(candidate) {
  // 取得最後一個事件
  const lastEvent = candidate.progressTracking?.[
    candidate.progressTracking.length - 1
  ];
  
  if (!lastEvent) {
    // 沒有進度記錄，用 createdAt
    return calculateDaysDiff(candidate.createdAt, today);
  }
  
  // 用最後一個事件的日期
  return calculateDaysDiff(lastEvent.date, today);
}

function calculateDaysDiff(startDate, endDate) {
  const start = new Date(startDate);
  const end = new Date(endDate);
  return Math.floor((end - start) / (1000 * 60 * 60 * 24));
}

// 範例
const candidate = {
  name: "王小明",
  status: "已聯繫",
  progressTracking: [
    { date: "2026-03-03", event: "未開始" },
    { date: "2026-03-04", event: "已聯繫" }  // 最後事件
  ]
};

const stayDays = calculateStayDays(candidate);  // 1 天
```

### 步驟 3：SLA 監控

```javascript
function checkSLA(candidate, today) {
  const config = SLA_CONFIG[candidate.status];
  
  // 終止狀態，無需監控
  if (config.is_terminal) {
    return { status: "terminal", alert: null };
  }
  
  const stayDays = calculateStayDays(candidate);
  const warningDays = config.warning_days;
  const thresholdDays = config.threshold_days;
  
  // 邏輯
  if (stayDays >= thresholdDays) {
    // 🔴 紅燈：SLA 已逾期
    return {
      status: "overdue",
      stayDays,
      alert: {
        level: "🔴 逾期",
        message: `${config.warning_message.replace("{name}", candidate.name)} (已逾期 ${stayDays - thresholdDays} 天)`,
        action: config.action,
        priority: "HIGH"
      }
    };
  }
  
  if (stayDays >= warningDays) {
    // ⚠️ 黃燈：即將逾期
    return {
      status: "warning",
      stayDays,
      alert: {
        level: "⚠️ 即將逾期",
        message: `${config.warning_message.replace("{name}", candidate.name)} (${thresholdDays - stayDays} 天後逾期)`,
        action: config.action,
        priority: "MEDIUM"
      }
    };
  }
  
  // 🟢 綠燈：正常
  return {
    status: "normal",
    stayDays,
    alert: null
  };
}

// 範例
const slaCheck = checkSLA(
  {
    name: "王小明",
    status: "已聯繫",
    progressTracking: [
      { date: "2026-03-01", event: "未開始" },
      { date: "2026-03-04", event: "已聯繫" }  // 3 天前
    ]
  },
  "2026-03-07"  // 今天
);

// 結果：
// {
//   status: "overdue",
//   stayDays: 3,
//   alert: {
//     level: "🔴 逾期",
//     message: "⚠️ 候選人王小明已聯繫 2 天，尚無回應 (已逾期 0 天)",
//     action: "主動追蹤",
//     priority: "HIGH"
//   }
// }
```

---

## 📋 四、每日掃描結果分類

### 掃描結果結構

```javascript
const scanResult = {
  scanDate: "2026-03-05",
  scanTime: "08:00:15",
  totalCandidates: 1234,
  
  // 按狀態分類
  byStatus: {
    "未開始": 45,
    "已聯繫": 123,
    "已面試": 87,
    "Offer": 12,
    "已上職": 234,
    "婉拒": 156,
    "備選人才": 577
  },
  
  // SLA 監控結果
  slaStatus: {
    normal: 1100,          // 🟢 正常進行
    warning: 98,           // ⚠️ 即將逾期
    overdue: 36            // 🔴 已逾期
  },
  
  // 詳細警告清單
  alerts: [
    {
      level: "🔴 逾期",
      count: 36,
      candidates: [
        {
          id: 123,
          name: "王小明",
          status: "已聯繫",
          stayDays: 4,
          slaDays: 3,
          urgency: "HIGH",
          action: "主動追蹤"
        },
        // ...more
      ]
    },
    {
      level: "⚠️ 即將逾期",
      count: 98,
      candidates: [
        {
          id: 456,
          name: "李大華",
          status: "已面試",
          stayDays: 6,
          slaDays: 7,
          urgency: "MEDIUM",
          action: "跟進結果"
        },
        // ...more
      ]
    }
  ],
  
  // 漏斗統計
  funnel: {
    "未開始 → 已聯繫": "37.8%",  // 多少人從「未開始」進展到「已聯繫」
    "已聯繫 → 已面試": "70.7%",
    "已面試 → Offer": "13.8%",
    "Offer → 已上職": "95.0%",
    "最終成功率": "3.8%"        // 已上職 / 總人數
  }
};
```

---

## 📤 五、通知規則

### 5.1 SLA 逾期通知（立即）

**觸發條件**：發現任何 SLA 逾期的候選人

**通知目標**：Telegram `HR AI招募自動化` Topic #4

**通知格式**：
```
🔴【SLA 逾期警告】2026-03-05 08:00

發現 36 位候選人 SLA 逾期！

❌ 已聯繫超過 3 天：
1. 王小明（ID: 123）- 逾期 1 天 → 主動追蹤
2. 李四（ID: 124）- 逾期 2 天 → 主動追蹤
...（最多顯示 5 個，有省略號表示更多）

❌ 已面試超過 7 天：
1. 陳五（ID: 125）- 逾期 1 天 → 跟進結果
2. 王六（ID: 126）- 逾期 3 天 → 跟進結果

🔗 前往系統查看完整清單 → Kanban 看板

建議操作：
1. 優先聯繫紅色標記的候選人
2. 更新進度或標記婉拒
3. 防止漏斗堵塞
```

### 5.2 即將逾期警告（06:00 - 提前 2 小時）

**觸發條件**：發現候選人距離 SLA 還有 0-2 天

**通知目標**：Telegram `HR AI招募自動化` Topic #4

**通知格式**：
```
⚠️【即將逾期提醒】2026-03-05 06:00

98 位候選人距離 SLA 逾期還有 0-2 天！

⏰ 已聯繫（即將逾期 3 天）：
1. 張三（ID: 201）- 還有 1 天 → 準備跟進
2. 李四（ID: 202）- 還有 2 天 → 準備跟進

⏰ 已面試（即將逾期 7 天）：
1. 王五（ID: 203）- 還有 1 天 → 準備決策

🔗 前往系統查看完整清單

建議操作：準備明日的跟進計劃
```

### 5.3 每日匯報（21:00）

**觸發條件**：每天傍晚

**通知目標**：龍蝦社群 Topic 15 + 發財基地

**通知格式**：
```
📊 Pipeline 日報 (2026-03-05) Jacky

✅ 今日進度
- 新增候選人：12 位
- 轉為「已聯繫」：8 位
- 轉為「已面試」：3 位
- 發出 Offer：2 位
- 新到職：1 位

📈 當前進度
- 未開始：45 位
- 已聯繫：123 位
- 已面試：87 位
- Offer：12 位
- 已上職：234 位
- 總計：501 位在進行中

⚠️ SLA 監控
- 🔴 逾期：36 位（需立即跟進）
- ⚠️ 即將逾期：98 位（明日需準備）
- 🟢 正常：1100 位

📉 漏斗進度
- 招聘成功率：3.8%（已上職 / 總人數）
- 面試通過率：13.8%（Offer / 已面試）

🎯 明日建議
1. 優先跟進 36 位逾期候選人
2. 準備 98 位即將逾期的跟進計劃
3. 確認 2 位 Offer 簽署進度
```

---

## 💾 六、狀態存儲

### memory/pipeline-state.json

```json
{
  "lastScanTime": "2026-03-05T08:00:15Z",
  "lastScanDate": "2026-03-05",
  
  "lastScanResult": {
    "totalCandidates": 1234,
    "slaStatus": {
      "normal": 1100,
      "warning": 98,
      "overdue": 36
    },
    "byStatus": {
      "未開始": 45,
      "已聯繫": 123,
      "已面試": 87,
      "Offer": 12,
      "已上職": 234,
      "婉拒": 156,
      "備選人才": 577
    }
  },
  
  "overdueAlerts": [
    {
      "id": 123,
      "name": "王小明",
      "status": "已聯繫",
      "stayDays": 4,
      "slaDays": 3,
      "lastAlertTime": "2026-03-05T08:00:15Z",
      "alertCount": 1
    }
  ],
  
  "warningAlerts": [
    {
      "id": 456,
      "name": "李大華",
      "status": "已面試",
      "stayDays": 6,
      "slaDays": 7,
      "lastAlertTime": "2026-03-05T06:00:00Z",
      "alertCount": 1
    }
  ],
  
  "notifiedCandidates": {
    "2026-03-05": {
      "overdue": [123, 124, 125],    // 已通知的逾期候選人
      "warning": [456, 457, 458]     // 已通知的警告候選人
    }
  }
}
```

---

## 🔄 七、Cron 任務配置

### 7.1 晨間掃描（08:00）

**Cron 表達式**：`0 8 * * *`

**執行內容**：
```bash
#!/bin/bash

# 1. 取得所有候選人
curl -s https://backendstep1ne.zeabur.app/api/candidates?limit=1000 \
  > /tmp/candidates_$(date +%Y%m%d_%H%M%S).json

# 2. 執行 SLA 掃描（由 AI 處理）
# → 計算停留天數
# → 檢查 SLA 閾值
# → 生成警告清單
# → 存儲到 memory/pipeline-state.json

# 3. 推送通知
# → 有紅燈：推送 SLA 逾期警告到 Topic #4
# → 推送日報初稿

# 4. 更新狀態文件
date > /Users/user/clawd/hr-tools/data/pipeline-last-scan.txt
```

### 7.2 傍晚提醒（18:00）

**Cron 表達式**：`0 18 * * *`

**執行內容**：
```bash
#!/bin/bash

# 1. 重新掃描一次（掌握最新狀態）
# 2. 確認有無新增逾期
# 3. 提醒明日即將逾期的候選人
```

### 7.3 每日匯報（21:00）

**Cron 表達式**：`0 21 * * *`

**執行內容**：
```bash
#!/bin/bash

# 1. 整理全天數據
# 2. 計算進度統計 + 漏斗
# 3. 推送日報到龍蝦社群 + 發財基地
```

### 7.4 每小時輕掃（09:00-20:00，每小時）

**Cron 表達式**：`0 9-20 * * *`

**執行內容**：
```bash
#!/bin/bash

# 輕掃（只檢查新增和狀態變化）
# 不做完整掃描，節省資源
# 只推送「新增 SLA 逾期」的警告
```

---

## 🛠️ 八、API 呼叫流程（詳細版）

### 完整掃描流程

```python
import requests
import json
from datetime import datetime, timedelta

class PipelineTracker:
    def __init__(self, base_url="https://backendstep1ne.zeabur.app"):
        self.base_url = base_url
        self.sla_config = {
            "未開始": {"threshold": 2, "warning": 1},
            "已聯繫": {"threshold": 3, "warning": 2},
            "已面試": {"threshold": 7, "warning": 5},
            "Offer": {"threshold": 5, "warning": 3},
        }
    
    def scan_pipeline(self):
        """執行完整 Pipeline 掃描"""
        
        # 1. 取得所有候選人
        print("📥 正在取得候選人清單...")
        candidates = self.fetch_candidates()
        print(f"✅ 取得 {len(candidates)} 位候選人")
        
        # 2. 初始化結果
        scan_result = {
            "scanDate": datetime.now().isoformat(),
            "totalCandidates": len(candidates),
            "byStatus": {},
            "slaStatus": {"normal": 0, "warning": 0, "overdue": 0},
            "alerts": []
        }
        
        # 3. 遍歷每位候選人
        overdue_list = []
        warning_list = []
        
        for candidate in candidates:
            status = candidate.get("status", "未開始")
            
            # 統計按狀態
            scan_result["byStatus"][status] = scan_result["byStatus"].get(status, 0) + 1
            
            # 檢查 SLA
            sla_check = self.check_sla(candidate)
            
            if sla_check["status"] == "overdue":
                scan_result["slaStatus"]["overdue"] += 1
                overdue_list.append({
                    "id": candidate["id"],
                    "name": candidate["name"],
                    "status": status,
                    "stayDays": sla_check["stayDays"],
                    "alert": sla_check["alert"]
                })
            elif sla_check["status"] == "warning":
                scan_result["slaStatus"]["warning"] += 1
                warning_list.append({
                    "id": candidate["id"],
                    "name": candidate["name"],
                    "status": status,
                    "stayDays": sla_check["stayDays"],
                    "alert": sla_check["alert"]
                })
            else:
                scan_result["slaStatus"]["normal"] += 1
        
        # 4. 整理警告清單
        scan_result["alerts"] = [
            {
                "level": "🔴 逾期",
                "count": len(overdue_list),
                "candidates": sorted(overdue_list, key=lambda x: x["stayDays"], reverse=True)[:10]
            },
            {
                "level": "⚠️ 即將逾期",
                "count": len(warning_list),
                "candidates": sorted(warning_list, key=lambda x: x["stayDays"], reverse=True)[:10]
            }
        ]
        
        # 5. 計算漏斗
        scan_result["funnel"] = self.calculate_funnel(candidates)
        
        # 6. 保存狀態
        self.save_state(scan_result)
        
        # 7. 推送通知
        self.send_notifications(scan_result)
        
        return scan_result
    
    def fetch_candidates(self):
        """取得所有候選人"""
        response = requests.get(f"{self.base_url}/api/candidates?limit=1000")
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    
    def check_sla(self, candidate):
        """檢查單一候選人的 SLA"""
        status = candidate.get("status")
        
        # 終止狀態，無需檢查
        if status in ["已上職", "婉拒"]:
            return {"status": "terminal"}
        
        # 計算停留天數
        stay_days = self.calculate_stay_days(candidate)
        
        # 取得 SLA 配置
        config = self.sla_config.get(status, {})
        if not config:
            return {"status": "unknown"}
        
        threshold = config["threshold"]
        warning = config["warning"]
        
        # 判斷
        if stay_days >= threshold:
            return {
                "status": "overdue",
                "stayDays": stay_days,
                "alert": f"SLA 逾期 {stay_days - threshold} 天"
            }
        elif stay_days >= warning:
            return {
                "status": "warning",
                "stayDays": stay_days,
                "alert": f"即將逾期 {threshold - stay_days} 天"
            }
        else:
            return {
                "status": "normal",
                "stayDays": stay_days
            }
    
    def calculate_stay_days(self, candidate):
        """計算停留天數"""
        progress_tracking = candidate.get("progressTracking", [])
        
        if progress_tracking:
            last_event = progress_tracking[-1]
            event_date = datetime.fromisoformat(last_event["date"].replace("Z", "+00:00"))
        else:
            created_at = candidate.get("createdAt")
            event_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        today = datetime.now(event_date.tzinfo).date()
        return (today - event_date.date()).days
    
    def calculate_funnel(self, candidates):
        """計算招聘漏斗"""
        statuses = [c.get("status") for c in candidates]
        
        funnel = {
            "未開始": statuses.count("未開始"),
            "已聯繫": statuses.count("已聯繫"),
            "已面試": statuses.count("已面試"),
            "Offer": statuses.count("Offer"),
            "已上職": statuses.count("已上職"),
            "婉拒": statuses.count("婉拒")
        }
        
        # 計算轉化率
        total = len(candidates)
        funnel["成功率"] = f"{(funnel['已上職'] / total * 100):.1f}%" if total > 0 else "0%"
        
        return funnel
    
    def save_state(self, result):
        """保存掃描結果"""
        with open("/Users/user/clawd/hr-tools/data/pipeline-state.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def send_notifications(self, result):
        """推送通知"""
        # 推送 SLA 逾期警告（如果有）
        overdue_count = result["slaStatus"]["overdue"]
        if overdue_count > 0:
            self.send_alert(f"🔴 發現 {overdue_count} 位候選人 SLA 逾期", result["alerts"])
        
        # 推送即將逾期警告（如果有）
        warning_count = result["slaStatus"]["warning"]
        if warning_count > 0:
            self.send_alert(f"⚠️ 發現 {warning_count} 位候選人即將逾期", result["alerts"])
    
    def send_alert(self, title, alerts):
        """發送 Telegram 通知"""
        # 此部分由 message 工具處理
        print(f"📢 {title}")
        for alert_group in alerts:
            print(f"   {alert_group['level']}: {alert_group['count']} 位")


# 執行掃描
if __name__ == "__main__":
    tracker = PipelineTracker()
    result = tracker.scan_pipeline()
    print(f"\n✅ 掃描完成！詳見 pipeline-state.json")
```

---

## ⚙️ 九、異常處理

### 場景 1：API 連接失敗

```python
try:
    candidates = self.fetch_candidates()
except requests.ConnectionError:
    # 通知顧問：系統暫時無法連接
    self.send_alert("❌ Pipeline 掃描失敗：無法連接到 Step1ne 系統", {})
    # 記錄錯誤
    logger.error("API connection failed")
    # 重試（最多 3 次，間隔 10 分鐘）
    retry_count = 0
    while retry_count < 3:
        time.sleep(600)
        retry_count += 1
        try:
            candidates = self.fetch_candidates()
            break
        except:
            pass
```

### 場景 2：進度記錄遺漏

```python
# 問題：progressTracking 為空，無法確定停留天數
if not candidate.get("progressTracking"):
    # 降級方案：用 createdAt
    stay_days = self.calculate_stay_days_from_created(candidate)
    logger.warning(f"Candidate {candidate['id']} missing progressTracking, using createdAt")
```

### 場景 3：候選人狀態異常

```python
# 問題：status 不在標準清單中（比如 "備選人才" 或拼寫錯誤）
if status not in self.sla_config:
    # 標記為警告，人工審查
    logger.warning(f"Candidate {candidate['id']} has invalid status: {status}")
    # 推送人工審查提醒
```

### 場景 4：重複通知

```python
# 問題：同一位候選人重複推送警告
# 解決：用 notifiedCandidates 追蹤已通知過的人

state = self.load_state()
today = str(datetime.now().date())

if today not in state.get("notifiedCandidates", {}):
    state["notifiedCandidates"][today] = {"overdue": [], "warning": []}

for candidate in overdue_list:
    if candidate["id"] not in state["notifiedCandidates"][today]["overdue"]:
        # 推送通知
        self.send_alert(...)
        # 記錄已通知
        state["notifiedCandidates"][today]["overdue"].append(candidate["id"])
```

---

## 📊 十、監控儀表板（可選）

### 實時看板顯示內容

```
【Pipeline 即時監控】— 每 5 分鐘更新

┌─────────────────────────────────────────┐
│ 當前時間：2026-03-05 08:45:30            │
│ 上次掃描：2026-03-05 08:00:00            │
├─────────────────────────────────────────┤
│ 候選人進度分佈                            │
│  [未開始  ███░░░░░░░░░░] 45 (3.6%)      │
│  [已聯繫  ███████░░░░░░░░░░░░░░] 123 (9.9%)     │
│  [已面試  █████░░░░░░░░░░░░] 87 (7.0%)  │
│  [Offer   ██░░░░░░░░░░░░░░░░░░░░░░░] 12 (1.0%) │
│  [已上職  ██████████░░░░░░] 234 (18.9%)        │
│  [婉拒   ███████░░░░░░░░░░░░░░] 156 (12.6%) │
│  [備選   █████████████░░░░░░░░] 577 (46.6%) │
├─────────────────────────────────────────┤
│ SLA 監控                                 │
│  🟢 正常進行：1100 位                     │
│  ⚠️ 即將逾期：98 位  ← ⚡ 需要注意          │
│  🔴 已逾期：36 位    ← 🚨 需要立即行動     │
├─────────────────────────────────────────┤
│ 招聘漏斗                                 │
│  成功率：3.8%（234 已上職 / 1234 總數）  │
│  面試→Offer：13.8%（12 Offer / 87 面試）│
│  聯繫→面試：70.7%（87 面試 / 123 聯繫）  │
├─────────────────────────────────────────┤
│ 近期動作                                 │
│ ▪ 10 分鐘前：李大華 轉為「已面試」        │
│ ▪ 30 分鐘前：王小明 轉為「已聯繫」        │
│ ▪ 1 小時前：新增陳五（待評分）           │
└─────────────────────────────────────────┘
```

---

## ✅ 十一、實施檢查清單

### 準備工作

- [ ] 確認 Step1ne API 可正常訪問
- [ ] 測試候選人資料結構是否完整
- [ ] 準備 memory/pipeline-state.json 文件
- [ ] 配置 Telegram 通知頻道 (Topic #4)

### 開發工作

- [ ] 實現 SLA 監控邏輯
- [ ] 實現 Pipeline 掃描腳本
- [ ] 實現 Telegram 通知功能
- [ ] 實現狀態存儲機制
- [ ] 實現異常處理

### 測試工作

- [ ] 單元測試：計算停留天數邏輯
- [ ] 單元測試：SLA 判斷邏輯
- [ ] 集成測試：完整掃描流程
- [ ] 端到端測試：推送通知
- [ ] 壓力測試：大量候選人（1000+）

### 上線工作

- [ ] 配置 Cron 任務（4 個）
- [ ] 配置告警規則
- [ ] 與顧問溝通工作流程
- [ ] 定期檢查日誌
- [ ] 收集反饋並改進

---

## 📞 十二、故障排查指南

| 問題 | 原因 | 解決方案 |
|------|------|--------|
| 掃描結果不更新 | Cron 任務未執行 | 檢查 `openclaw cron list` |
| 通知沒有推送 | Telegram 認證失敗 | 檢查 token 是否有效 |
| SLA 計算錯誤 | progressTracking 為空 | 補充缺失的進度記錄 |
| 重複通知 | notifiedCandidates 狀態遺失 | 檢查 pipeline-state.json |
| API 超時 | 候選人數量過多 | 分頁取得，或增加超時時間 |

---

## 🎯 總結

這套 Pipeline 追蹤系統提供：

✅ **自動監控**：每天 4 次掃描，實時監控 SLA  
✅ **智能警告**：分級警告（紅/黃/綠），及時提醒  
✅ **數據統計**：漏斗分析，進度可視化  
✅ **狀態追蹤**：完整的進度記錄 + 操作日誌  
✅ **異常處理**：自動降級方案，確保系統穩定  

**預期效果**：
- 📉 招聘漏斗再不會「堵塞」
- ⚡ SLA 逾期「零遺漏」
- 📊 進度「實時可視」
- 🤖 工作「自動化」

---

**下一步**：要我幫你實現具體的 Python 腳本 / Node.js 代碼嗎？
