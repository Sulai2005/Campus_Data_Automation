"""Student routes - protected by student role"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Student
from auth.dependencies import require_student

router = APIRouter(prefix="/student", tags=["Student"])


@router.get("/dashboard")
def student_dashboard(
    current_user: dict = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Get student dashboard data (read-only).
    Student identity is derived from JWT token.
    """
    student = db.query(Student).filter(Student.email == current_user.get("sub")).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return {
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "department": student.department,
        "year": student.year,
        "phone": student.phone,
        "address": student.address
    }


@router.get("/profile")
def get_student_profile(
    current_user: dict = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Get detailed student profile.
    """
    student = db.query(Student).filter(Student.email == current_user.get("sub")).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return {
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "department": student.department,
        "year": student.year,
        "phone": student.phone,
        "address": student.address,
    }
