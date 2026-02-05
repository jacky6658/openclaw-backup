from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models import (
    StudyPlan,
    StudyPlanCreate,
    StudyPlanRead,
    StudyPlanWithTasks,
    StudyTask,
    StudyTaskCreate,
    StudyTaskRead,
)

router = APIRouter(prefix="/tenants/{tenant_id}", tags=["study_plans"])


@router.get(
    "/students/{student_id}/study-plan",
    response_model=StudyPlanWithTasks,
)
def get_active_study_plan(
    tenant_id: str,
    student_id: str,
    session: Session = Depends(get_session),
):
    plan = session.exec(
        select(StudyPlan)
        .where(StudyPlan.tenant_id == tenant_id)
        .where(StudyPlan.student_id == student_id)
        .where(StudyPlan.status == "ACTIVE")
    ).first()

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active plan")

    tasks: List[StudyTask] = session.exec(
        select(StudyTask).where(StudyTask.plan_id == plan.id).order_by(StudyTask.task_date, StudyTask.order_in_day)
    ).all()

    return StudyPlanWithTasks(
        plan=StudyPlanRead.from_orm(plan),
        tasks=[StudyTaskRead.from_orm(t) for t in tasks],
    )


@router.post(
    "/students/{student_id}/study-plan",
    status_code=status.HTTP_201_CREATED,
)
def create_or_replace_study_plan(
    tenant_id: str,
    student_id: str,
    payload: StudyPlanCreate,
    session: Session = Depends(get_session),
):
    # 1) 將舊的 ACTIVE 計畫標為 ARCHIVED
    old_plans = session.exec(
        select(StudyPlan)
        .where(StudyPlan.tenant_id == tenant_id)
        .where(StudyPlan.student_id == student_id)
        .where(StudyPlan.status == "ACTIVE")
    ).all()
    for p in old_plans:
        p.status = "ARCHIVED"
        p.updated_at = datetime.utcnow()
        session.add(p)

    planned_days = len(payload.tasks)
    planned_total_hours = sum(t.duration_hours for t in payload.tasks)

    plan = StudyPlan(
      tenant_id=tenant_id,
      student_id=student_id,
      course_id=None,
      title=payload.title,
      target_exam_date=payload.target_exam_date,
      start_date=payload.start_date,
      end_date=payload.end_date,
      created_by_role=payload.created_by_role,
      created_by_id=payload.created_by_id,
      planned_days=planned_days,
      planned_total_hours=planned_total_hours,
      status="ACTIVE",
      config_json={
          "weeklyDays": payload.weekly_days,
          "dailyHours": payload.daily_hours,
          "subject": payload.subject,
      },
    )
    session.add(plan)
    session.flush()  # 確保有 plan.id

    for idx, t in enumerate(payload.tasks, start=1):
        task = StudyTask(
            tenant_id=tenant_id,
            plan_id=plan.id,
            task_date=t.task_date,
            subject_code=t.subject_code,
            title=t.title,
            description=t.description,
            duration_hours=t.duration_hours,
            order_in_day=t.order_in_day or idx,
        )
        session.add(task)

    session.commit()

    return {"planId": plan.id, "createdTasks": planned_days}


@router.patch("/study-tasks/{task_id}", response_model=StudyTaskRead)
def update_task_status(
    tenant_id: str,
    task_id: int,
    body: dict,
    session: Session = Depends(get_session),
):
    task = session.get(StudyTask, task_id)
    if not task or task.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    status_value = body.get("status")
    if status_value:
        task.status = status_value
        if status_value == "DONE":
            task.completed_at = datetime.utcnow()

    if "duration_hours" in body:
        task.duration_hours = float(body["duration_hours"])

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    return StudyTaskRead.from_orm(task)


@router.delete("/students/{student_id}/study-plan", status_code=status.HTTP_204_NO_CONTENT)
def clear_active_plan(
    tenant_id: str,
    student_id: str,
    session: Session = Depends(get_session),
):
    plan = session.exec(
        select(StudyPlan)
        .where(StudyPlan.tenant_id == tenant_id)
        .where(StudyPlan.student_id == student_id)
        .where(StudyPlan.status == "ACTIVE")
    ).first()

    if not plan:
        return

    plan.status = "CANCELLED"
    plan.updated_at = datetime.utcnow()
    session.add(plan)
    session.commit()
