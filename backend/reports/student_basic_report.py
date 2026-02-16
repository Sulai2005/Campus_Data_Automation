"""
Student Basic Report Generator

This report generates a customizable student list with:
- Student ID (Register Number) - Always included
- Name - Always included
- Optional empty columns for manual data entry

Users can specify how many empty columns they want to include.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import Student


def generate_student_basic_report(
    db: Session,
    department: Optional[str] = None,
    year: Optional[int] = None,
    empty_columns: int = 0
) -> dict:
    """
    Generate a basic student report with register number and name
    
    Args:
        db: Database session
        department: Optional filter by department
        year: Optional filter by year
        empty_columns: Number of empty columns to include (0-5)
    
    Returns:
        Dictionary containing report data and metadata
    """
    
    # Build query
    query = db.query(Student)
    
    # Apply filters
    if department:
        query = query.filter(Student.department == department)
    if year:
        query = query.filter(Student.year == year)
    
    # Order by student_id
    query = query.order_by(Student.student_id)
    
    # Execute query
    students = query.all()
    
    # Limit empty columns to reasonable range
    empty_columns = max(0, min(empty_columns, 5))
    
    # Build column headers
    columns = ["Register Number", "Name"]
    
    # Add empty column headers
    for i in range(empty_columns):
        columns.append(f"Column {i + 1}")
    
    # Build data rows
    rows = []
    for student in students:
        row = {
            "Register Number": student.student_id,
            "Name": student.name
        }
        
        # Add empty columns
        for i in range(empty_columns):
            row[f"Column {i + 1}"] = ""
        
        rows.append(row)
    
    # Build filter description
    filters_desc = []
    if department:
        filters_desc.append(f"Department: {department}")
    if year:
        filters_desc.append(f"Year: {year}")
    filter_text = " | ".join(filters_desc) if filters_desc else "No filters"
    
    # Build response
    return {
        "report_name": "Student Basic Report",
        "description": f"Student register numbers and names. Filters: {filter_text}",
        "columns": columns,
        "data": rows,
        "total_records": len(rows),
        "filters": {
            "department": department,
            "year": year,
            "empty_columns": empty_columns
        }
    }

