# EduMind API (FastAPI + Postgres)

這是你的 EduMind 後端骨架，使用 **FastAPI + SQLModel + Postgres**。

> 資料表與 API 設計對應 `docs/study-plans-api.md` 中的 `study_plans` / `study_tasks` 規格。

---

## 1. 專案結構

```text
edumind-api/
  ├─ main.py                # FastAPI 入口，掛載 study_plans 路由
  ├─ database.py            # DB 連線與 init_db()
  ├─ models.py              # StudyPlan / StudyTask 及相關 Pydantic models
  ├─ routes_study_plans.py  # 讀書計畫相關 API
  ├─ requirements.txt       # Python 套件需求
  └─ README.md              # 本說明
```

---

## 2. 前置條件

- 需要有一個 Postgres instance
  - 開發環境可以用本機：`postgres://postgres:postgres@localhost:5432/edumind`
  - 或自己用 docker 起一個 Postgres：

```bash
docker run --name edumind-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=edumind -p 5432:5432 -d postgres:16
```

- 在 `edumind-api` 資料夾中，`.env`（可選）：

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/edumind
```

若未設定，會預設用上面這個連線字串。

---

## 3. 安裝依賴

```bash
cd edumind-api
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## 4. 建立資料表

啟動時 `main.py` 的 `on_startup` 會呼叫 `init_db()`，
第一次啟動時會自動在資料庫中建立 `study_plans` / `study_tasks` 兩張表。

若想手動初始化，也可以在 Python REPL 中：

```bash
python
>>> from database import init_db
>>> init_db()
```

---

## 5. 啟動開發伺服器

```bash
cd edumind-api
uvicorn main:app --reload
```

啟動後：
- 健康檢查：<http://localhost:8000/>
- API 文件：<http://localhost:8000/docs>

---

## 6. 可用的 API（對應規格）

Base path：`/tenants/{tenant_id}`

### 1) 取得學生目前有效的讀書計畫

**GET** `/tenants/{tenant_id}/students/{student_id}/study-plan`

- 若有 ACTIVE 計畫 → 回傳 `StudyPlanWithTasks`
- 若沒有 → 回 404

### 2) 建立 / 覆蓋一份新的讀書計畫

**POST** `/tenants/{tenant_id}/students/{student_id}/study-plan`

Body 範例（簡化）：

```json
{
  "title": "本週 Python 讀書計畫",
  "target_exam_date": "2026-01-15",
  "start_date": "2025-12-18",
  "end_date": "2025-12-24",
  "weekly_days": 3,
  "daily_hours": 1.5,
  "subject": "python",
  "created_by_role": "student",
  "created_by_id": null,
  "tasks": [
    {
      "task_date": "2025-12-18",
      "subject_code": "python",
      "title": "複習第 1 章 + 習題 1-1 ~ 1-5",
      "duration_hours": 1.5
    }
  ]
}
```

回應範例：

```json
{"planId": 1, "createdTasks": 3}
```

### 3) 更新單一任務狀態

**PATCH** `/tenants/{tenant_id}/study-tasks/{task_id}`

Body 範例：

```json
{"status": "DONE"}
```

或：

```json
{"status": "DONE", "duration_hours": 2.0}
```

回應：該任務的最新資料。

### 4) 清除目前計畫

**DELETE** `/tenants/{tenant_id}/students/{student_id}/study-plan`

- 找到 ACTIVE 計畫 → status 改為 `CANCELLED`
- 回 `204 No Content`

---

## 7. 後續可以怎麼接前端？

- 學生端 StudyCoachView：
  - 產生計畫時 → 呼叫 `POST /tenants/{tenant}/students/{student}/study-plan`
  - 載入頁面時 → 呼叫 `GET /tenants/{tenant}/students/{student}/study-plan`
  - 勾選任務時 → 呼叫 `PATCH /tenants/{tenant}/study-tasks/{taskId}`
  - 清除計畫時 → 呼叫 `DELETE /tenants/{tenant}/students/{student}/study-plan`

這樣就能把現在的 localStorage 流程，逐步換成真正的後端 API。
