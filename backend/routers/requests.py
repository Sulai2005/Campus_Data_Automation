from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from database.db import get_db
from database.models import User, Student, UpdateRequest, AuditLog
from auth.dependencies import require_admin, require_student

router = APIRouter(prefix="/requests", tags=["Update Requests"])

# Pydantic models for request body
class RequestCreate(BaseModel):
    field_name: str
    new_value: str
    reason: str

class RequestUpdate(BaseModel):
    status: str # 'approved' or 'rejected'
    feedback: Optional[str] = None

class RequestResponse(BaseModel):
    id: int
    field_name: str
    old_value: Optional[str]
    new_value: str
    status: str
    reason: str
    feedback: Optional[str]
    requested_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
    
    model_config = {"from_attributes": True}

# Whitelist of editable fields
EDITABLE_FIELDS = ['name', 'department', 'year', 'phone', 'address']

# --------------------------------------------------------------------------------
# Student Endpoints
# --------------------------------------------------------------------------------

@router.post("/", response_model=RequestResponse)
def create_request(
    request: RequestCreate,
    current_user: dict = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Student: Create a new update request.
    Only allows updating specific fields: name, department, year, phone, address.
    """
    # 1. Validate field name
    if request.field_name not in EDITABLE_FIELDS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid field. You can only request updates for: {', '.join(EDITABLE_FIELDS)}"
        )
        
    # 2. Find the Student record associated with the current user (by email in 'sub')
    email = current_user.get("sub")
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found for this user.")

    # 3. Check for pending requests for the same field
    existing_pending = db.query(UpdateRequest).filter(
        UpdateRequest.student_id == student.id,
        UpdateRequest.field_name == request.field_name,
        UpdateRequest.status == "pending"
    ).first()
    
    if existing_pending:
        raise HTTPException(
            status_code=400,
            detail=f"You already have a pending request for '{request.field_name}'. Please wait for it to be reviewed."
        )

    # 4. Get old value
    old_val = str(getattr(student, request.field_name)) if getattr(student, request.field_name) is not None else ""

    # 5. Create UpdateRequest
    new_request = UpdateRequest(
        student_id=student.id,
        field_name=request.field_name,
        old_value=old_val,
        new_value=request.new_value,
        reason=request.reason,
        status="pending"
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return new_request

@router.get("/my", response_model=List[RequestResponse])
def get_my_requests(
    current_user: dict = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Student: Get all my update requests.
    """
    email = current_user.get("sub")
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
        
    requests = db.query(UpdateRequest).filter(UpdateRequest.student_id == student.id).order_by(UpdateRequest.requested_at.desc()).all()
    return requests

# --------------------------------------------------------------------------------
# Admin Endpoints
# --------------------------------------------------------------------------------

@router.get("/all", response_model=List[Dict[str, Any]]) 
def get_all_requests(
    status_filter: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: Get all requests (optionally filtered by status).
    Returns request details + student name/id.
    """
    query = db.query(UpdateRequest)
    
    if status_filter:
        query = query.filter(UpdateRequest.status == status_filter)
        
    requests = query.order_by(UpdateRequest.requested_at.desc()).all()
    
    # Custom response to include student info
    result = []
    for req in requests:
        student = db.query(Student).filter(Student.id == req.student_id).first()
        result.append({
            "id": req.id,
            "student_id": student.student_id if student else "Unknown",
            "student_name": student.name if student else "Unknown",
            "field_name": req.field_name,
            "old_value": req.old_value,
            "new_value": req.new_value,
            "reason": req.reason,
            "status": req.status,
            "feedback": req.feedback,
            "requested_at": req.requested_at,
            "reviewed_at": req.reviewed_at,
            "reviewed_by": req.reviewed_by
        })
    
    return result

@router.put("/{request_id}/status")
def update_request_status(
    request_id: int,
    update_data: RequestUpdate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: Approve or Reject a request.
    If Approved, updates the Student record automatically.
    """
    # 1. Get request
    req = db.query(UpdateRequest).filter(UpdateRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {req.status}")
        
    # 2. Update request status
    req.status = update_data.status
    req.feedback = update_data.feedback
    req.reviewed_at = datetime.utcnow()
    req.reviewed_by = current_user.get("sub")
    
    # 3. If Approved, update Student record
    if update_data.status == "approved":
        student = db.query(Student).filter(Student.id == req.student_id).first()
        if student:
            # Set new value
            val_to_set = req.new_value
            if req.field_name == 'year':
                try:
                    val_to_set = int(val_to_set)
                except:
                    pass 
            
            setattr(student, req.field_name, val_to_set)
            
            # Create Audit Log
            # We need user model for ID, find user by email
            admin_user = db.query(User).filter(User.email == current_user.get("sub")).first()
            audit = AuditLog(
                user_id=admin_user.id if admin_user else None,
                user_email=current_user.get("sub"),
                action="approve_update",
                entity_type="student",
                entity_id=student.id,
                old_value=req.old_value,
                new_value=str(val_to_set)
            )
            db.add(audit)

    db.commit()
    return {"message": f"Request {update_data.status} successfully"}
