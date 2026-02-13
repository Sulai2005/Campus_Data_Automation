from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


class User(Base):
    """User authentication and role management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'staff', 'student'
    created_at = Column(DateTime, default=datetime.utcnow)


class Student(Base):
    """Core student identity and information"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    department = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("StudentDocument", back_populates="student", cascade="all, delete-orphan")
    update_requests = relationship("UpdateRequest", back_populates="student", cascade="all, delete-orphan")


class StudentDocument(Base):
    """Photo and document metadata storage"""
    __tablename__ = "student_documents"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    file_type = Column(String, nullable=False)  # 'photo', 'certificate', 'id_proof', etc.
    file_path = Column(String, nullable=False)  # Relative path to file
    file_name = Column(String, nullable=False)  # Original filename
    uploaded_by = Column(String, nullable=False)  # Email of uploader
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="documents")


class AuditLog(Base):
    """Immutable audit trail for sensitive actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String, nullable=False)
    action = Column(String, nullable=False)  # 'create', 'update', 'delete', 'approve', 'reject'
    entity_type = Column(String, nullable=False)  # 'student', 'document', 'update_request'
    entity_id = Column(Integer, nullable=True)
    old_value = Column(Text, nullable=True)  # JSON string
    new_value = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class UpdateRequest(Base):
    """Student update request workflow"""
    __tablename__ = "update_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    field_name = Column(String, nullable=False)  # Field to be updated
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=False)
    status = Column(String, default="pending")  # 'pending', 'approved', 'rejected', 'applied'
    reason = Column(Text, nullable=True)  # Reason for request
    feedback = Column(Text, nullable=True)  # Staff feedback
    
    requested_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)  # Email of reviewer
    
    # Relationships
    student = relationship("Student", back_populates="update_requests")
