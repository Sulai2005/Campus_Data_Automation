"""Report generation service"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from database.models import Student


def generate_student_report(
    db: Session,
    department: Optional[str] = None,
    year: Optional[int] = None
) -> List[Dict]:
    """
    Generate student report with optional filters
    
    Args:
        db: Database session
        department: Filter by department (optional)
        year: Filter by year (optional)
    
    Returns:
        List of student records matching filters
    """
    # Build query
    query = db.query(Student)
    
    # Apply filters
    if department:
        from database.models import Department
        query = query.join(Student.department_rel).filter(Department.name == department)
    
    if year:
        query = query.filter(Student.year == year)
    
    # Execute query
    students = query.all()
    
    # Format results
    report_data = []
    for student in students:
        report_data.append({
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email,
            "department": student.department,
            "year": student.year,
            "phone": student.phone,
            "created_at": student.created_at.isoformat() if student.created_at else None
        })
    
    return report_data


def get_report_statistics(db: Session) -> Dict:
    """
    Get basic statistics for reporting dashboard
    
    Args:
        db: Database session
    
    Returns:
        Dictionary with statistics
    """
    total_students = db.query(Student).count()
    
    # Count by department
    from database.models import Department
    departments = db.query(Department.name).distinct().all()
    department_counts = {}
    for (dept,) in departments:
        if dept:
            count = db.query(Student).join(Student.department_rel).filter(Department.name == dept).count()
            department_counts[dept] = count
    
    return {
        "total_students": total_students,
        "department_breakdown": department_counts
    }
