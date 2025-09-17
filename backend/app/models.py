from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class Semester(Base):
    __tablename__ = "semesters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    courses = relationship("Course", back_populates="semester", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False)
    sr_no = Column(Integer, nullable=False)
    course_code = Column(String(30), nullable=False)
    course_name = Column(String(200), nullable=False)
    credit_hours = Column(Integer, nullable=False)
    semester = relationship("Semester", back_populates="courses")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    roll_no = Column(String(50), nullable=False, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    total_ch = Column(Integer, nullable=False)
    total_gp = Column(Float, nullable=False)
    gpa = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    items = relationship("SubmissionItem", back_populates="submission", cascade="all, delete-orphan")

class SubmissionItem(Base):
    __tablename__ = "submission_items"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    grade_point = Column(Float, nullable=False)
    total_gp = Column(Float, nullable=False)
    submission = relationship("Submission", back_populates="items")