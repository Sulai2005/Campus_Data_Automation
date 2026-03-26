
import csv
import io
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from database.models import Student

def process_student_csv(file_content: bytes, db: Session) -> Dict[str, Any]:
    """
    Process CSV file content and create students.
    Expected headers: student_id, name, department, year, email, phone, address
    'email' is optional; if missing, defaults to {student_id}@placeholder.com
    """
    # Use TextIOWrapper for proper newline handling
    text_stream = io.TextIOWrapper(io.BytesIO(file_content), encoding='utf-8')
    reader = csv.DictReader(text_stream)
    
    # Normalize headers
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="Empty CSV file")
        
    # Map headers to lowercase stripped
    field_map = {name: name.lower().strip() for name in reader.fieldnames}
    reverse_map = {v: k for k, v in field_map.items()}
    
    # Check required
    required_fields = {'student_id', 'name'}
    found_fields = set(field_map.values())
    
    missing = required_fields - found_fields
    if missing:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required columns: {', '.join(missing)}"
        )
        
    created_count = 0
    updated_count = 0
    errors = []
    
    for row_idx, row in enumerate(reader, start=1):
        try:
            # Helper to get value using normalized header name
            def get_val(key):
                original_key = reverse_map.get(key)
                return row.get(original_key, '').strip()
                
            student_id = get_val('student_id')
            name = get_val('name')
            
            if not student_id or not name:
                errors.append(f"Row {row_idx}: Missing student_id or name")
                continue
                
            dept = get_val('department') or None
            year_str = get_val('year')
            year = int(year_str) if year_str and year_str.isdigit() else None
            phone = get_val('phone') or None
            address = get_val('address') or None
            email = get_val('email')
            
            # Default email if missing
            if not email:
                email = f"{student_id}@placeholder.com"
                
            # Check existing
            existing = db.query(Student).filter(Student.student_id == student_id).first()
            
            if existing:
                # Update
                existing.name = name
                existing.department = dept
                existing.year = year
                existing.phone = phone
                existing.address = address
                # Only update email if provided and not placeholder
                if email and "placeholder.com" not in email:
                    existing.email = email
                updated_count += 1
            else:
                # Create
                # Check if email is already taken by ANOTHER student (collision check)
                email_check = db.query(Student).filter(Student.email == email).first()
                if email_check:
                    # Append index to make unique or skip?
                    # Skip for now to avoid mess
                    errors.append(f"Row {row_idx}: Email {email} already used by another student")
                    continue
                    
                new_student = Student(
                    student_id=student_id,
                    name=name,
                    email=email,
                    department=dept,
                    year=year,
                    phone=phone,
                    address=address
                )
                db.add(new_student)
                created_count += 1
                
            db.commit() # Commit each row to allow partial success
        except Exception as e:
            db.rollback() # Rollback only this failed transaction
            errors.append(f"Row {row_idx} (ID {student_id}): {str(e)}")
            # Continue to next row
            
    return {
        "created": created_count,
        "updated": updated_count,
        "errors": errors
    }
