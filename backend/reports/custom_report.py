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
from sqlalchemy import inspect, Table, MetaData, select
from database.models import Student, DataSchema


def get_available_columns(db: Session, schema_id: Optional[int] = None) -> Dict[str, str]:
    """
    Dynamically get all available columns from Student model or from a dynamic schema table.
    """
    columns = {}
    
    if schema_id:
        schema = db.query(DataSchema).filter(DataSchema.id == schema_id).first()
        if not schema or not schema.target_table:
            raise ValueError("Invalid schema_id or missing target table")
            
        metadata = MetaData()
        target_table = Table(schema.target_table, metadata, autoload_with=db.get_bind())
        
        exclude_columns = ['id', 'created_at', 'updated_at']
        for column in target_table.columns:
            if column.name not in exclude_columns:
                columns[column.name] = column.name.replace('_', ' ').title()
        return columns

    # Legacy static fallback to Student model
    inspector = inspect(Student)
    
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
    exclude_columns = ['id', 'created_at', 'updated_at', 'department_id']
    
    for column in inspector.columns:
        col_name = column.name
        if col_name not in exclude_columns:
            columns[col_name] = display_names.get(col_name, col_name.replace('_', ' ').title())
            
    # Include the proxy column explicitly
    columns['department'] = 'Department' 
    
    return columns


def generate_custom_report(
    db: Session,
    selected_columns: List[str],
    department: Optional[str] = None,
    year: Optional[int] = None,
    empty_columns: int = 0,
    custom_column_names: Optional[List[str]] = None,
    schema_id: Optional[int] = None
) -> dict:
    """
    Generate a custom report with user-selected columns off a dynamic schema table.
    """
    
    # Get available columns
    available_columns_dict = get_available_columns(db, schema_id)
    available_columns = list(available_columns_dict.keys())
    
    # Validate selected columns
    invalid_columns = [col for col in selected_columns if col not in available_columns]
    if invalid_columns:
        raise ValueError(f"Invalid columns: {', '.join(invalid_columns)}")
    
    # Build query
    if schema_id:
        schema = db.query(DataSchema).filter(DataSchema.id == schema_id).first()
        metadata = MetaData()
        target_table = Table(schema.target_table, metadata, autoload_with=db.get_bind())
        
        # Build core select query
        query = select(target_table)
        
        # Apply filters optionally if the dynamically generated table happens to have them
        if department and 'department' in target_table.c:
            query = query.where(target_table.c.department == department)
        if year and 'year' in target_table.c:
            query = query.where(target_table.c.year == year)
            
        result = db.execute(query)
        # Convert core row cursor into a list of dicts mapped to column names
        students = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        
    else:
        # Legacy static ORM behavior
        query = db.query(Student)
        if department:
            from database.models import Department
            query = query.join(Student.department_rel).filter(Department.name == department)
        if year:
            query = query.filter(Student.year == year)
        query = query.order_by(Student.student_id)
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
            if isinstance(student, dict):
                value = student.get(col, '')
            else:
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
