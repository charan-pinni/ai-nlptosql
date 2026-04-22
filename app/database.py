from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import random

SQLALCHEMY_DATABASE_URL = "sqlite:///./edtech.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(models.Student).first():
            return
            
        # Seed Students (10)
        students = []
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"]
        for name in names:
            student = models.Student(name=name, grade=random.uniform(70.0, 100.0))
            db.add(student)
            students.append(student)
        db.commit()

        # Seed Courses (5)
        courses = []
        course_data = [
            ("Python", "Programming"),
            ("Machine Learning", "AI"),
            ("Data Science", "Data"),
            ("Web Development", "Programming"),
            ("SQL Databases", "Data")
        ]
        for name, category in course_data:
            course = models.Course(name=name, category=category)
            db.add(course)
            courses.append(course)
        db.commit()

        # Seed Enrollments (20)
        # Ensure 2024 data exists
        import datetime as dt
        for _ in range(20):
            student = random.choice(students)
            course = random.choice(courses)
            # Random date in 2023 or 2024
            year = random.choice([2023, 2024])
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            enrolled_at = dt.datetime(year, month, day)
            
            enrollment = models.Enrollment(
                student_id=student.id,
                course_id=course.id,
                enrolled_at=enrolled_at
            )
            db.add(enrollment)
        db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
