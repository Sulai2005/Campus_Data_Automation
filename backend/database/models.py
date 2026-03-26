from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime

from .db import Base


class Department(Base):
    """Normalized department lookup"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    # Relationships
    students = relationship("Student", back_populates="department_rel")


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
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    year = Column(Integer, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department_rel = relationship("Department", back_populates="students")
    update_requests = relationship("UpdateRequest", back_populates="student", cascade="all, delete-orphan")

    # Seamlessly map old .department string property to the relation
    department = association_proxy("department_rel", "name", creator=lambda n: Department(name=n))


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


# ─────────────────────────────────────────────────
# Dynamic Data Ingestion Engine Models
# ─────────────────────────────────────────────────

class DataSchema(Base):
    """Admin-defined schema: a named collection of typed fields."""
    __tablename__ = "data_schemas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    target_table = Column(String, nullable=True)  # new spec
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fields = relationship("SchemaField", back_populates="schema", cascade="all, delete-orphan")
    uploaded_data = relationship("UploadedData", back_populates="schema")


class SchemaField(Base):
    """A single typed field belonging to a DataSchema."""
    __tablename__ = "schema_fields"

    id = Column(Integer, primary_key=True, index=True)
    schema_id = Column(Integer, ForeignKey("data_schemas.id"), nullable=False)
    field_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False, default="string")  # string|int|float|date|boolean
    is_required = Column(Boolean, default=False)
    
    # Normalization metadata
    is_foreign_key = Column(Boolean, default=False)
    reference_table = Column(String, nullable=True)       # e.g., "departments"
    reference_field = Column(String, nullable=True)       # e.g., "name"
    target_column = Column(String, nullable=True)         # actual column on target_table, e.g., "department_id"
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    schema = relationship("DataSchema", back_populates="fields")


class UploadSession(Base):
    """Tracks an in-progress or completed upload: file stored temp until mapping confirmed."""
    __tablename__ = "upload_sessions"

    id = Column(Integer, primary_key=True, index=True)
    schema_id = Column(Integer, ForeignKey("data_schemas.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    temp_file_path = Column(String, nullable=False)
    detected_columns = Column(Text, nullable=True)   # JSON list of column names
    status = Column(String, default="pending")        # pending | mapped | ingested | failed
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mappings = relationship("ColumnMapping", back_populates="session", cascade="all, delete-orphan")


class ColumnMapping(Base):
    """Maps one Excel/CSV column to one SchemaField for a given UploadSession."""
    __tablename__ = "column_mappings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("upload_sessions.id"), nullable=False)
    excel_column = Column(String, nullable=False)     # e.g. "Student Name"
    field_id = Column(Integer, ForeignKey("schema_fields.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("UploadSession", back_populates="mappings")
    field = relationship("SchemaField")


class UploadedData(Base):
    """Single-table JSON storage for all ingested rows from any schema."""
    __tablename__ = "uploaded_data"

    id = Column(Integer, primary_key=True, index=True)
    schema_id = Column(Integer, ForeignKey("data_schemas.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("upload_sessions.id"), nullable=True)
    data = Column(Text, nullable=False)               # JSON string: {"field": value, ...}
    row_index = Column(Integer, nullable=True)         # Original row number in the file
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    schema = relationship("DataSchema", back_populates="uploaded_data")
