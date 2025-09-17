from pydantic import BaseModel, Field
from typing import List

class CourseOut(BaseModel):
    id: int
    sr_no: int
    course_code: str
    course_name: str
    credit_hours: int
    class Config:
        orm_mode = True

class SemesterOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class GradeItemIn(BaseModel):
    course_id: int
    grade_point: float = Field(ge=0.0, le=4.0)

class SubmissionIn(BaseModel):
    name: str
    roll_no: str
    semester_id: int
    grades: List[GradeItemIn]

class SubmissionOut(BaseModel):
    id: int
    name: str
    roll_no: str
    semester_id: int
    total_ch: int
    total_gp: float
    gpa: float
    class Config:
        orm_mode = True