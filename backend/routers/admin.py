"""Admin routes - protected by admin role"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database.db import get_db
from auth.dependencies import require_admin
from services.report_service import generate_student_report

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def admin_dashboard(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin dashboard endpoint (placeholder)
    
    Returns:
        Dashboard metadata
    """
    
    # Get stats
    total_students = db.query(Student).count()
    pending_requests = db.query(UpdateRequest).filter(UpdateRequest.status == "pending").count()
    
    return {
        "message": "Admin Dashboard",
        "user": current_user.get("sub"),
        "role": current_user.get("role"),
        "stats": {
            "total_students": total_students,
            "pending_requests": pending_requests
        }
    }


@router.post("/upload/data")
def upload_data(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Legacy bulk import student data from CSV (deprecated - use /api/ingestion endpoints).
    Kept for backward compatibility.
    """
    from services.import_service import process_student_csv
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    try:
        content = file.file.read()
        result = process_student_csv(content, db)
        return {"message": "Data processed successfully", "summary": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reports/generate")
def generate_report(
    department: Optional[str] = None,
    year: Optional[int] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Generate student report with optional filters
    
    Args:
        department: Filter by department
        year: Filter by year
        current_user: Current authenticated admin user
        db: Database session
    
    Returns:
        Report data
    """
    report_data = generate_student_report(
        db=db,
        department=department,
        year=year
    )
    
    return {
        "message": "Report generated successfully",
        "filters": {
            "department": department,
            "year": year
        },
        "data": report_data
    }

from auth.hashing import Hash
from database.models import Student, User, UpdateRequest
from pydantic import BaseModel

class UserCredentials(BaseModel):
    email: str
    password: str

@router.get("/students")
def get_students(
    department: Optional[str] = None,
    year: Optional[int] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of students with filtering
    """
    query = db.query(Student)
    
    if department:
        from database.models import Department
        query = query.join(Student.department_rel).filter(Department.name == department)
    if year:
        query = query.filter(Student.year == year)
        
    students = query.order_by(Student.student_id).all()
    
    result = []
    for s in students:
        # Check if user account exists
        user = db.query(User).filter(User.email == s.email).first()
        result.append({
            "id": s.id,
            "student_id": s.student_id,
            "name": s.name,
            "email": s.email,
            "department": s.department,
            "year": s.year,
            "has_account": user is not None
        })
        
    return result

@router.post("/students/{student_id}/credentials")
def assign_credentials(
    student_id: int,
    credentials: UserCredentials,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Assign email and password to a student (creates/updates User account)
    """
    # 1. Get student
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # 2. Update student email if changed
    if credentials.email != student.email:
        # Check if email taken by another student
        existing = db.query(Student).filter(Student.email == credentials.email, Student.id != student_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already used by another student")
        student.email = credentials.email
        
    # 3. Create or Update User account
    user = db.query(User).filter(User.email == credentials.email).first()
    if user:
        # Update existing user
        user.hashed_password = Hash.bcrypt(credentials.password)
    else:
        # Create new user
        # Check if old email user exists (if email changed)
        # For simplicity, we assume we are creating a new user or updating the one matching the email.
        # If student had a different email before, that old user account is orphaned or needs update?
        # A better approach: Find user by ID? No, User and Student are loosely coupled by email.
        # So we just ensure a User exists with this email and password.
        
        new_user = User(
            email=credentials.email,
            hashed_password=Hash.bcrypt(credentials.password),
            role="student"
        )
        db.add(new_user)
        
    db.commit()
    
    return {"message": "Credentials assigned successfully"}
