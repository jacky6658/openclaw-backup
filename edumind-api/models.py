from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class StudyPlanBase(SQLModel):
    tenant_id: str = Field(index=True)
    student_id: str = Field(index=True)
    course_id: Optional[str] = Field(default=None, index=True)

    title: str
    target_exam_date: Optional[date] = None
    start_date: date
    end_date: date

    created_by_role: str = "student"  # student | teacher | ai | admin
    created_by_id: Optional[str] = None

    planned_days: int
    planned_total_hours: float

    status: str = Field(default="ACTIVE")  # ACTIVE | ARCHIVED | CANCELLED | COMPLETED
    config_json: Optional[dict] = None


class StudyPlan(StudyPlanBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    tasks: list[StudyTask] = Relationship(back_populates="plan")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StudyTaskBase(SQLModel):
    tenant_id: str = Field(index=True)
    task_date: date = Field(index=True)
    subject_code: str
    title: str
    description: Optional[str] = None
    duration_hours: float
    order_in_day: int = 1

    status: str = Field(default="PENDING")  # PENDING | IN_PROGRESS | DONE | SKIPPED
    source: str = Field(default="manual")   # manual | ai_suggestion | teacher_template
    metadata: Optional[dict] = None


class StudyTask(StudyTaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="studyplan.id", index=True)

    completed_at: Optional[datetime] = None

    plan: Optional[StudyPlan] = Relationship(back_populates="tasks")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Response / payload models

class StudyTaskCreate(SQLModel):
    task_date: date
    subject_code: str
    title: str
    description: Optional[str] = None
    duration_hours: float
    order_in_day: int = 1


class StudyTaskRead(SQLModel):
    id: int
    task_date: date
    subject_code: str
    title: str
    description: Optional[str] = None
    duration_hours: float
    order_in_day: int
    status: str


class StudyPlanCreate(SQLModel):
    title: str
    target_exam_date: Optional[date] = None
    start_date: date
    end_date: date

    weekly_days: int
    daily_hours: float
    subject: str

    created_by_role: str = "student"
    created_by_id: Optional[str] = None

    tasks: list[StudyTaskCreate]


class StudyPlanRead(SQLModel):
    id: int
    title: str
    target_exam_date: Optional[date]
    start_date: date
    end_date: date
    planned_days: int
    planned_total_hours: float
    status: str
    config_json: Optional[dict]


class StudyPlanWithTasks(SQLModel):
    plan: StudyPlanRead
    tasks: list[StudyTaskRead]
