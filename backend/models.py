from datetime import date
from enum import Enum
from pydantic import BaseModel, Field


class AssignmentType(str, Enum):
    HOMEWORK = "homework"
    EXAM = "exam"
    PROJECT = "project"
    QUIZ = "quiz"
    OTHER = "other"


class Course(BaseModel):
    name: str
    code: str


class Assignment(BaseModel):
    name: str
    course: str
    due_date: date
    assignment_type: AssignmentType


class WeeklyWorkload(BaseModel):
    week_start_date: date
    week_end_date: date
    assignment_count: int
    intensity_score: float
    assignments_by_type: dict[str, int] = Field(default_factory=dict)
