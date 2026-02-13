"""File upload service - handles file storage and metadata"""

import os
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from database.models import Student, StudentDocument

# Upload directory configuration
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types and max size
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


async def save_uploaded_file(
    file: UploadFile,
    student_id: int,
    file_type: str,
    uploaded_by: str,
    db: Session
) -> dict:
    """
    Save uploaded file to disk and store metadata in database
    
    Args:
        file: Uploaded file object
        student_id: ID of the student
        file_type: Type of file (photo, certificate, etc.)
        uploaded_by: Email of the uploader
        db: Database session
    
    Returns:
        Dictionary with file metadata
    
    Raises:
        HTTPException: If validation fails
    """
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{student.student_id}_{file_type}_{timestamp}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store metadata in database
    document = StudentDocument(
        student_id=student_id,
        file_type=file_type,
        file_path=file_path,
        file_name=file.filename,
        uploaded_by=uploaded_by
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return {
        "id": document.id,
        "student_id": student.student_id,
        "file_type": file_type,
        "file_name": file.filename,
        "file_path": file_path,
        "uploaded_at": document.uploaded_at.isoformat()
    }
