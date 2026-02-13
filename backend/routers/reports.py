"""Reports router - Handle all report generation endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.db import get_db
from auth.dependencies import require_admin
from reports.student_basic_report import generate_student_basic_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/student-basic")
def get_student_basic_report(
    department: Optional[str] = Query(None, description="Filter by department"),
    year: Optional[int] = Query(None, ge=1, le=4, description="Filter by year (1-4)"),
    empty_columns: int = Query(0, ge=0, le=5, description="Number of empty columns to include (0-5)"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Generate a basic student report with register number and name
    
    This report includes:
    - Student ID (Register Number)
    - Student Name
    - Optional empty columns for manual data entry
    
    **Filters:**
    - department: Filter students by department
    - year: Filter students by year (1-4)
    - empty_columns: Add empty columns for manual data (0-5)
    
    **Access:** Admin only
    """
    
    report = generate_student_basic_report(
        db=db,
        department=department,
        year=year,
        empty_columns=empty_columns
    )
    
    return report


@router.get("/available")
def get_available_reports(current_user: dict = Depends(require_admin)):
    """
    Get list of available reports
    
    **Access:** Admin only
    """
    
    return {
        "reports": [
            {
                "id": "student-basic",
                "name": "Student Basic Report",
                "description": "Register numbers and names with optional empty columns",
                "endpoint": "/reports/student-basic",
                "parameters": {
                    "department": "Optional - Filter by department",
                    "year": "Optional - Filter by year (1-4)",
                    "empty_columns": "Optional - Number of empty columns (0-5)"
                }
            }
        ]
    }
