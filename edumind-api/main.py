from fastapi import FastAPI

from database import init_db
from routes_study_plans import router as study_plans_router

app = FastAPI(title="EduMind API", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    # 初始化資料表（開發環境用；正式環境可改成 migration 工具）
    init_db()


@app.get("/")
async def read_root() -> dict:
    return {"status": "ok", "service": "edumind-api"}


app.include_router(study_plans_router)
