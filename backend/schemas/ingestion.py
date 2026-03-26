"""Pydantic v2 schemas for Dynamic Data Ingestion Engine."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ─────────────────────────────────────────────────
# Schema Field models
# ─────────────────────────────────────────────────

class SchemaFieldCreate(BaseModel):
    field_name: str = Field(..., min_length=1, max_length=100)
    data_type: str = Field(default="string", pattern="^(string|int|float|date|boolean)$")
    is_required: bool = False

    # Normalization metadata
    is_foreign_key: bool = False
    reference_table: Optional[str] = None
    reference_field: Optional[str] = None
    target_column: Optional[str] = None


class SchemaFieldOut(BaseModel):
    id: int
    schema_id: int
    field_name: str
    data_type: str
    is_required: bool
    
    is_foreign_key: bool
    reference_table: Optional[str]
    reference_field: Optional[str]
    target_column: Optional[str]
    
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────
# DataSchema models
# ─────────────────────────────────────────────────

class DataSchemaCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_table: Optional[str] = None
    fields: List[SchemaFieldCreate]


class DataSchemaOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    target_table: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    fields: List[SchemaFieldOut]

    model_config = {"from_attributes": True}


class DataSchemaListItem(BaseModel):
    """Compact schema representation for lists."""
    id: int
    name: str
    description: Optional[str]
    field_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────
# Upload Session models
# ─────────────────────────────────────────────────

class UploadPreviewResponse(BaseModel):
    """Returned after a file is uploaded: shows detected columns + schema info."""
    session_id: int
    schema_id: int
    schema_name: str
    original_filename: str
    detected_columns: List[str]
    schema_fields: List[SchemaFieldOut]


# ─────────────────────────────────────────────────
# Column Mapping & Ingest models
# ─────────────────────────────────────────────────

class MapAndIngestRequest(BaseModel):
    """Frontend sends this after user defines the column→field mapping."""
    session_id: int
    schema_id: int
    # key = excel column name, value = schema field_name (not field id)
    mapping: Dict[str, str]
    duplicate_mode: str = Field(default="skip", description="skip | update | error | preview")


class RowError(BaseModel):
    row_index: int
    column: str
    message: str


class IngestResult(BaseModel):
    rows_inserted: int
    rows_updated: int = 0
    rows_skipped: int = 0
    duplicates_found: int = 0
    errors: List[RowError]
    warnings: List[str]
    audit_log_id: Optional[int]


# ─────────────────────────────────────────────────
# Stored data retrieval
# ─────────────────────────────────────────────────

class UploadedDataRow(BaseModel):
    id: int
    schema_id: int
    session_id: Optional[int]
    row_index: Optional[int]
    data: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
