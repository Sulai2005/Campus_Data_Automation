"""
Custom Report Generator

This report allows users to:
- Select any combination of columns from the Student model
- Add custom empty columns with editable names
- Filter by department and year
- Fully dynamic and modular
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from database.models import Student


def get_available_columns() -> Dict[str, str]:
    """
    Dynamically get all available columns from Student model
    
    Returns:
        Dictionary mapping column names to display labels
    """
    inspector = inspect(Student)
    columns = {}
    
    # Define display names for columns
    display_names = {
        'student_id': 'Student ID',
        'name': 'Name',
        'email': 'Email',
        'department': 'Department',
        'year': 'Year',
        'phone': 'Phone',
        'address': 'Address'
    }
    
    # Exclude internal columns
    exclude_columns = ['id', 'created_at', 'updated_at']
    
    for column in inspector.columns:
        col_name = column.name
        if col_name not in exclude_columns:
            columns[col_name] = display_names.get(col_name, col_name.replace('_', ' ').title())
    
    return columns


def generate_custom_report(
    db: Session,
    selected_columns: List[str],
    department: Optional[str] = None,
    year: Optional[int] = None,
    empty_columns: int = 0,
    custom_column_names: Optional[List[str]] = None
) -> dict:
    """
    Generate a custom report with user-selected columns
    
    Args:
        db: Database session
        selected_columns: List of column names to include
        department: Optional filter by department
        year: Optional filter by year
        empty_columns: Number of empty columns to add (0-10)
        custom_column_names: Optional list of custom names for empty columns
    
    Returns:
        Dictionary containing report data and metadata
    """
    
    # Get available columns
    available_columns_dict = get_available_columns()
    available_columns = list(available_columns_dict.keys())
    
    # Validate selected columns
    invalid_columns = [col for col in selected_columns if col not in available_columns]
    if invalid_columns:
        raise ValueError(f"Invalid columns: {', '.join(invalid_columns)}")
    
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
    empty_columns = max(0, min(empty_columns, 10))
    
    # Build column headers
    columns = [available_columns_dict[col] for col in selected_columns]
    
    # Add empty columns with custom or default names
    if custom_column_names and len(custom_column_names) >= empty_columns:
        # Use custom names
        for i in range(empty_columns):
            col_name = custom_column_names[i].strip() if custom_column_names[i].strip() else f"Custom {i + 1}"
            columns.append(col_name)
    else:
        # Use default names
        for i in range(empty_columns):
            columns.append(f"Custom {i + 1}")
    
    # Build data rows
    report_data = []
    for student in students:
        row = {}
        
        # Add selected columns
        for col in selected_columns:
            display_label = available_columns_dict[col]
            value = getattr(student, col, '')
            row[display_label] = value if value is not None else ''
        
        # Add empty columns
        if custom_column_names and len(custom_column_names) >= empty_columns:
            for i in range(empty_columns):
                col_name = custom_column_names[i].strip() if custom_column_names[i].strip() else f"Custom {i + 1}"
                row[col_name] = ""
        else:
            for i in range(empty_columns):
                row[f"Custom {i + 1}"] = ""
        
        report_data.append(row)
    
    # Build filter description
    filters_desc = []
    if department:
        filters_desc.append(f"Department: {department}")
    if year:
        filters_desc.append(f"Year: {year}")
    if empty_columns > 0:
        filters_desc.append(f"{empty_columns} custom column(s)")
    filter_text = " | ".join(filters_desc) if filters_desc else "No filters"
    
    return {
        "report_name": "Custom Student Report",
        "description": f"Custom report with selected columns. Filters: {filter_text}",
        "columns": columns,
        "data": report_data,
        "total_records": len(report_data),
        "filters": {
            "department": department,
            "year": year,
            "empty_columns": empty_columns
        }
    }
