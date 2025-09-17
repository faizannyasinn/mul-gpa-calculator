from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import Base, engine, get_db
from .models import Semester, Course, Submission, SubmissionItem
from .schemas import SemesterOut, CourseOut, SubmissionIn, SubmissionOut
from .seed import seed

app = FastAPI(title="MUL GPA Calculator API", version="1.0.0")

# CORS (allow your Vercel frontend domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Seed semesters and courses
    db = next(get_db())
    seed(db, Semester, Course)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/semesters", response_model=List[SemesterOut])
def list_semesters(db: Session = Depends(get_db)):
    return db.query(Semester).order_by(Semester.id).all()

@app.get("/api/semesters/{semester_id}/courses", response_model=List[CourseOut])
def get_courses(semester_id: int, db: Session = Depends(get_db)):
    sem = db.query(Semester).filter(Semester.id == semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found")
    return (
        db.query(Course)
        .filter(Course.semester_id == semester_id)
        .order_by(Course.sr_no)
        .all()
    )

@app.post("/api/submit", response_model=SubmissionOut)
def submit(sub: SubmissionIn, db: Session = Depends(get_db)):
    # Validate courses and compute totals
    course_ids = [g.course_id for g in sub.grades]
    if not course_ids:
        raise HTTPException(status_code=400, detail="Grades list is empty")
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
    if len(courses) != len(course_ids):
        raise HTTPException(status_code=400, detail="One or more course_id invalid")

    # All courses must belong to the given semester
    semester_ids = {c.semester_id for c in courses}
    if len(semester_ids) != 1 or list(semester_ids)[0] != sub.semester_id:
        raise HTTPException(status_code=400, detail="Courses do not match semester_id")

    ch_map = {c.id: c.credit_hours for c in courses}
    total_gp = 0.0
    total_ch = 0

    for g in sub.grades:
        ch = ch_map[g.course_id]
        total_gp += float(g.grade_point) * int(ch)
        total_ch += int(ch)

    gpa = round(total_gp / total_ch, 2) if total_ch else 0.0

    submission = Submission(
        name=sub.name,
        roll_no=sub.roll_no,
        semester_id=sub.semester_id,
        total_ch=total_ch,
        total_gp=round(total_gp, 2),
        gpa=gpa,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    for g in sub.grades:
        db.add(
            SubmissionItem(
                submission_id=submission.id,
                course_id=g.course_id,
                grade_point=float(g.grade_point),
                total_gp=float(g.grade_point) * int(ch_map[g.course_id]),
            )
        )
    db.commit()

    return submission