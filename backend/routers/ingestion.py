"""
Ingestion Router – API endpoints for the Dynamic Data Ingestion Engine.

Endpoints:
  GET  /api/ingestion/schemas            – List all schemas
  POST /api/ingestion/schemas            – Create a new schema + fields (admin only)
  POST /api/ingestion/upload             – Upload file, get detected columns back
  POST /api/ingestion/upload/map         – Submit column mapping and ingest data
  GET  /api/ingestion/data/{schema_id}   – View stored rows for a schema
"""

import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import DataSchema, SchemaField, UploadSession, UploadedData
from auth.dependencies import require_admin, get_current_user
from schemas.ingestion import (
    DataSchemaCreate, DataSchemaOut, DataSchemaListItem,
    UploadPreviewResponse, SchemaFieldOut,
    MapAndIngestRequest, IngestResult,
    UploadedDataRow,
)
from services.ingestion_service import (
    save_temp_file, extract_columns, ingest_data
)

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


# ─────────────────────────────────────────────────
# Helper: require admin OR staff
# ─────────────────────────────────────────────────

def require_staff_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Access denied. Admin or Staff role required.")
    return current_user


# ─────────────────────────────────────────────────
# GET /api/ingestion/schemas
# ─────────────────────────────────────────────────

@router.get("/schemas", response_model=List[DataSchemaOut])
def list_schemas(
    current_user: dict = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """Return all schemas with their fields."""
    schemas = db.query(DataSchema).order_by(DataSchema.created_at.desc()).all()
    return schemas


from sqlalchemy import Table, MetaData, Column, Integer, String, Float, Date
from sqlalchemy.orm import Session
from datetime import datetime
import re

# ─────────────────────────────────────────────────
# POST /api/ingestion/schemas
# ─────────────────────────────────────────────────

@router.post("/schemas", response_model=DataSchemaOut, status_code=201)
def create_schema(
    payload: DataSchemaCreate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin creates a new schema with fields, and generates a dynamic table."""
    # Name uniqueness check
    existing = db.query(DataSchema).filter(DataSchema.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Schema named '{payload.name}' already exists.")

    # Generate a safe target_table name
    safe_name = "dynamic_" + re.sub(r'[^a-zA-Z0-9]', '_', payload.name.lower())
    
    # 1. Start Building the Dynamic SQLAlchemy Table
    metadata = MetaData()
    columns = [
        Column('id', Integer, primary_key=True, autoincrement=True),
    ]

    for field_data in payload.fields:
        safe_col_name = re.sub(r'[^a-zA-Z0-9]', '_', field_data.field_name.lower())
        
        # Map generic UI types to SQLAlchemy types
        col_type = String
        if field_data.data_type == 'int':
            col_type = Integer
        elif field_data.data_type == 'float':
            col_type = Float
        elif field_data.data_type == 'date':
            col_type = Date
            
        columns.append(Column(safe_col_name, col_type, nullable=not field_data.is_required))

    # Add required metadata
    columns.append(Column('created_at', String, default=lambda: datetime.utcnow().isoformat()))
    columns.append(Column('updated_at', String, default=lambda: datetime.utcnow().isoformat()))

    dynamic_table = Table(safe_name, metadata, *columns)

    try:
        # Physically create the table in SQLite
        dynamic_table.create(bind=db.get_bind())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to provision dynamic table: {e}")

    # 2. Save the metadata layout into DataSchema rules engine
    schema = DataSchema(
        name=payload.name,
        description=payload.description,
        created_by=current_user.get("user_id"),
        target_table=safe_name  # The new dynamic table acts as the permanent target
    )
    db.add(schema)
    db.flush()

    for field_data in payload.fields:
        safe_col_name = re.sub(r'[^a-zA-Z0-9]', '_', field_data.field_name.lower())
        field = SchemaField(
            schema_id=schema.id,
            field_name=field_data.field_name,
            target_column=safe_col_name, # Map exactly to created physical column
            data_type=field_data.data_type,
            is_required=field_data.is_required,
        )
        db.add(field)

    db.commit()
    db.refresh(schema)
    return schema


# ─────────────────────────────────────────────────
# DELETE /api/ingestion/schemas/{schema_id}
# ─────────────────────────────────────────────────

@router.delete("/schemas/{schema_id}", status_code=200)
def delete_schema(
    schema_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin deletes a schema and all its data."""
    schema = db.query(DataSchema).filter(DataSchema.id == schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found.")
    db.delete(schema)
    db.commit()
    return {"message": f"Schema '{schema.name}' and all associated data deleted."}


# ─────────────────────────────────────────────────
# POST /api/ingestion/upload
# Step 1: Upload file → get detected columns + schema fields
# ─────────────────────────────────────────────────

@router.post("/upload", response_model=UploadPreviewResponse)
async def upload_file(
    schema_id: int = Form(..., description="ID of the schema this file belongs to"),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """
    Step 1 of the ingestion flow.
    Saves the file to temp storage, detects column names, returns them
    alongside schema fields so the frontend can render a mapping UI.
    """
    user_id = current_user.get("user_id")
    session = await save_temp_file(file, schema_id, user_id, db)

    # Detect columns
    columns = extract_columns(session.temp_file_path)

    # Update session with detected columns
    session.detected_columns = json.dumps(columns)
    db.commit()

    # Load schema + fields
    schema = db.query(DataSchema).filter(DataSchema.id == schema_id).first()
    fields = db.query(SchemaField).filter(SchemaField.schema_id == schema_id).all()

    return UploadPreviewResponse(
        session_id=session.id,
        schema_id=schema.id,
        schema_name=schema.name,
        original_filename=session.original_filename,
        detected_columns=columns,
        schema_fields=[SchemaFieldOut.model_validate(f) for f in fields],
    )


# ─────────────────────────────────────────────────
# POST /api/ingestion/upload/map
# Step 2: Submit mapping + trigger ingest
# ─────────────────────────────────────────────────

@router.post("/upload/map", response_model=IngestResult)
def map_and_ingest(
    payload: MapAndIngestRequest,
    current_user: dict = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """
    Step 2 of the ingestion flow.
    Accepts the column → field mapping, runs validation,
    stores rows as JSON, writes audit log.
    """
    if not payload.mapping:
        raise HTTPException(status_code=400, detail="Mapping cannot be empty.")

    result = ingest_data(
        session_id=payload.session_id,
        schema_id=payload.schema_id,
        mapping=payload.mapping,
        current_user=current_user,
        db=db,
        duplicate_mode=payload.duplicate_mode,
    )
    return result


# ─────────────────────────────────────────────────
# GET /api/ingestion/data/{schema_id}
# ─────────────────────────────────────────────────

@router.get("/data/{schema_id}")
def get_schema_data(
    schema_id: int,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    session_id: Optional[int] = Query(default=None),
    current_user: dict = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """
    Retrieve ingested rows for a given schema.
    Supports pagination and optional session_id filter.
    """
    schema = db.query(DataSchema).filter(DataSchema.id == schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found.")

    query = db.query(UploadedData).filter(UploadedData.schema_id == schema_id)
    if session_id:
        query = query.filter(UploadedData.session_id == session_id)

    total = query.count()
    rows = query.order_by(UploadedData.id).offset(offset).limit(limit).all()

    return {
        "schema_id": schema_id,
        "schema_name": schema.name,
        "total": total,
        "offset": offset,
        "limit": limit,
        "rows": [
            {
                "id": r.id,
                "session_id": r.session_id,
                "row_index": r.row_index,
                "data": json.loads(r.data),
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ],
    }


# ─────────────────────────────────────────────────
# GET /api/ingestion/sessions/{session_id}
# ─────────────────────────────────────────────────

@router.get("/sessions/{session_id}")
def get_session(
    session_id: int,
    current_user: dict = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """Get details of an upload session."""
    session = db.query(UploadSession).filter(UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "id": session.id,
        "schema_id": session.schema_id,
        "original_filename": session.original_filename,
        "status": session.status,
        "detected_columns": json.loads(session.detected_columns) if session.detected_columns else [],
        "created_at": session.created_at.isoformat(),
    }
