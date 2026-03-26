"""Reports router - Handle all report generation endpoints"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Optional, List

from database.db import get_db
from database.models import Student
from auth.dependencies import require_admin
from reports.student_basic_report import generate_student_basic_report

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_student_columns():
    """
    Dynamically get all available columns from Student model
    Returns dict with column names and their display labels
    """
    inspector = inspect(Student)
    columns = {}
    
    # Define display names for columns (can be customized)
    display_names = {
        'id': 'Database ID',
        'student_id': 'Student ID',
        'name': 'Name',
        'email': 'Email',
        'department': 'Department',
        'year': 'Year',
        'phone': 'Phone',
        'address': 'Address',
        'created_at': 'Created Date',
        'updated_at': 'Updated Date'
    }
    
    # Exclude internal columns
    exclude_columns = ['id', 'created_at', 'updated_at']
    
    for column in inspector.columns:
        col_name = column.name
        if col_name not in exclude_columns:
            columns[col_name] = display_names.get(col_name, col_name.replace('_', ' ').title())
    
    return columns


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


@router.get("/columns")
def get_available_columns_route(
    schema_id: Optional[int] = Query(None, description="Schema ID to load dynamic columns from"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all available columns dynamically based on schema_id.
    """
    from reports.custom_report import get_available_columns
    
    try:
        columns = get_available_columns(db=db, schema_id=schema_id)
        return {
            "columns": [
                {
                    "name": col_name,
                    "label": label,
                    "type": "string"
                }
                for col_name, label in columns.items()
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/custom")
def get_custom_report(
    columns: str = Query(..., description="Comma-separated list of columns to include"),
    department: Optional[str] = Query(None, description="Filter by department"),
    year: Optional[int] = Query(None, ge=1, le=4, description="Filter by year (1-4)"),
    empty_columns: int = Query(0, ge=0, le=10, description="Number of empty columns to add (0-10)"),
    custom_column_names: Optional[str] = Query(None, description="Comma-separated custom names for empty columns"),
    schema_id: Optional[int] = Query(None, description="ID of dynamic schema to query"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Generate a custom report dynamically based on schema_id.
    """
    
    # Import here to avoid circular imports
    from reports.custom_report import generate_custom_report
    
    # Parse selected columns
    selected_columns = [col.strip() for col in columns.split(',')]
    
    # Parse custom column names if provided
    custom_names = None
    if custom_column_names:
        custom_names = [name.strip() for name in custom_column_names.split(',')]
    
    try:
        report = generate_custom_report(
            db=db,
            selected_columns=selected_columns,
            department=department,
            year=year,
            empty_columns=empty_columns,
            custom_column_names=custom_names,
            schema_id=schema_id
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/departments")
def get_departments(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Get all unique departments from the database dynamically
    
    **Access:** Admin only
    """
    from database.models import Department
    departments = db.query(Department.name).distinct().filter(Department.name.isnot(None)).all()
    return {
        "departments": [dept[0] for dept in departments if dept[0]]
    }


@router.get("/available")
def get_available_reports(current_user: dict = Depends(require_admin)):
    """
    Get list of available reports
    
    **Access:** Admin only
    """
    
    # Get available columns dynamically
    columns = get_student_columns()
    
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
            },
            {
                "id": "custom",
                "name": "Custom Report",
                "description": "Select specific columns to include in the report",
                "endpoint": "/reports/custom",
                "parameters": {
                    "columns": "Required - Comma-separated column names",
                    "department": "Optional - Filter by department",
                    "year": "Optional - Filter by year (1-4)"
                },
                "available_columns": [
                    {"name": col_name, "label": label}
                    for col_name, label in columns.items()
                ]
            }
        ]
    }
