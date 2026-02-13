"""Admin routes - protected by admin role"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database.db import get_db
from auth.dependencies import require_admin
from services.upload_service import save_uploaded_file
from services.report_service import generate_student_report

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def admin_dashboard(current_user: dict = Depends(require_admin)):
    """
    Admin dashboard endpoint (placeholder)
    
    Returns:
        Dashboard metadata
    """
    return {
        "message": "Admin Dashboard",
        "user": current_user.get("sub"),
        "role": current_user.get("role")
    }


@router.post("/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    student_id: int = Form(...),
    file_type: str = Form(...),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Upload a file (photo, document, etc.) for a student
    
    Args:
        file: Uploaded file
        student_id: ID of the student
        file_type: Type of file (photo, certificate, id_proof, etc.)
        current_user: Current authenticated admin user
        db: Database session
    
    Returns:
        Upload result with file metadata
    """
    result = await save_uploaded_file(
        file=file,
        student_id=student_id,
        file_type=file_type,
        uploaded_by=current_user.get("sub"),
        db=db
    )
    
    return {
        "message": "File uploaded successfully",
        "file_info": result
    }


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
