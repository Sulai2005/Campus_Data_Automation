"""
Ingestion Service – Core engine for schema-driven data ingestion.

Responsibilities:
  1. save_temp_file()         – Persist uploaded file to uploads/tmp/
  2. extract_columns()        – Detect column names via pandas
  3. validate_and_transform() – Apply mapping, validate types, build JSON rows
  4. ingest_data()            – Orchestrate: transform → bulk insert → audit log
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

import pandas as pd
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from database.models import (
    DataSchema, SchemaField, UploadSession,
    ColumnMapping, UploadedData, AuditLog, Student
)
from schemas.ingestion import RowError, IngestResult

logger = logging.getLogger(__name__)

TEMP_DIR = os.path.join("uploads", "tmp")
os.makedirs(TEMP_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ─────────────────────────────────────────────────
# 1. Save uploaded file to temp storage
# ─────────────────────────────────────────────────

async def save_temp_file(
    file: UploadFile,
    schema_id: int,
    user_id: Optional[int],
    db: Session
) -> UploadSession:
    """
    Saves the uploaded CSV/Excel to a temp path and creates an UploadSession.
    Returns the UploadSession ORM object (status=pending, columns not yet set).
    """
    # Extension check
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds maximum allowed size of 10MB.")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Verify schema exists
    schema = db.query(DataSchema).filter(DataSchema.id == schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail=f"Schema with id={schema_id} not found.")

    # Persist to disk
    unique_name = f"{uuid.uuid4().hex}{ext}"
    temp_path = os.path.join(TEMP_DIR, unique_name)
    with open(temp_path, "wb") as f:
        f.write(content)

    session = UploadSession(
        schema_id=schema_id,
        original_filename=file.filename,
        temp_file_path=temp_path,
        status="pending",
        uploaded_by=user_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# ─────────────────────────────────────────────────
# 2. Extract column names from the file
# ─────────────────────────────────────────────────

def _load_file_dataframe(file_path: str) -> Tuple[pd.DataFrame, int]:
    """
    Loads CSV/Excel robustly. Scans the first 20 rows to find the actual header row
    (the row with the most non-null values, assuming titles/blank rows come first).
    Returns (DataFrame, header_row_index).
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == ".csv":
            df_raw = pd.read_csv(file_path, header=None, nrows=20, keep_default_na=False)
        else:
            df_raw = pd.read_excel(file_path, header=None, nrows=20, engine="openpyxl")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {e}")
        
    best_row_idx = 0
    max_non_null = 0
    for i, row in df_raw.iterrows():
        # count cells that aren't NaN/None or completely empty strings
        non_null_count = sum(1 for val in row if pd.notna(val) and str(val).strip() != "")
        if non_null_count > max_non_null:
            max_non_null = non_null_count
            best_row_idx = i
            
    try:
        if ext == ".csv":
            df = pd.read_csv(file_path, header=best_row_idx, dtype=str, keep_default_na=False)
        else:
            df = pd.read_excel(file_path, header=best_row_idx, dtype=str, engine="openpyxl", keep_default_na=False)
            
        # Detect and coalesce vertically merged multi-row headers
        new_columns = list(df.columns)
        merged_header_detected = False
        
        for i, col in enumerate(new_columns):
            if str(col).startswith("Unnamed: ") and len(df) > 0:
                val = df.iloc[0, i]
                if pd.notna(val) and str(val).strip() != "":
                    new_columns[i] = str(val).strip()
                    merged_header_detected = True
                    
        df.columns = new_columns
        
        if merged_header_detected:
            # The first data row was actually the second half of the merged header
            df = df.iloc[1:].reset_index(drop=True)
            
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not extract data from file: {e}")
        
    return df, best_row_idx

def extract_columns(file_path: str) -> List[str]:
    """Reads the file and returns actual detected column names."""
    df, _ = _load_file_dataframe(file_path)
    # Ignore pandas autogenerated 'Unnamed: X' columns and fully empty column strings
    return [str(c).strip() for c in df.columns.tolist() if not str(c).startswith("Unnamed:") and str(c).strip()]


# ─────────────────────────────────────────────────
# 3. Validate and transform rows
# ─────────────────────────────────────────────────

def _coerce_value(raw: Any, data_type: str) -> Any:
    """Attempt to coerce a raw cell value to the declared data type."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None

    raw_str = str(raw).strip()
    if raw_str == "" or raw_str.lower() == "nan":
        return None

    if data_type == "int":
        try:
            return int(float(raw_str))
        except (ValueError, TypeError):
            raise ValueError(f"Expected integer, got '{raw_str}'")

    if data_type == "float":
        try:
            return float(raw_str)
        except (ValueError, TypeError):
            raise ValueError(f"Expected number, got '{raw_str}'")

    if data_type == "date":
        try:
            # Parse flexibly but return a native python date object for strict SQLAlchemy binding
            parsed = pd.to_datetime(raw_str, format='mixed', dayfirst=True)
            return parsed.date()
        except Exception:
            raise ValueError(f"Expected date, got '{raw_str}'")

    if data_type == "boolean":
        if raw_str.lower() in ("1", "true", "yes"):
            return True
        if raw_str.lower() in ("0", "false", "no"):
            return False
        raise ValueError(f"Expected boolean (true/false/yes/no/1/0), got '{raw_str}'")

    # default: string
    return raw_str


def validate_and_transform(
    db: Session,
    file_path: str,
    mapping: Dict[str, str],          # excel_col → field_name
    fields: List[SchemaField],
) -> Tuple[List[Dict[str, Any]], List[RowError]]:
    """
    Reads the full file, applies mapping, validates types, resolves foreign keys dynamically,
    and checks required fields. Returns (valid_rows, errors).
    """
    df, header_offset = _load_file_dataframe(file_path)

    # Build lookup: field_name → SchemaField object
    field_lookup: Dict[str, SchemaField] = {f.field_name: f for f in fields}
    # Reverse: excel_col → field_name (from user mapping)
    # mapping = {"Student Name": "name", "Marks": "score"}

    valid_rows: List[Dict[str, Any]] = []
    errors: List[RowError] = []

    for row_idx, row in df.iterrows():
        row_data: Dict[str, Any] = {}
        row_errors: List[RowError] = []

        for excel_col, field_name in mapping.items():
            field = field_lookup.get(field_name)
            if not field:
                continue  # mapping references non-existent field → skip silently

            # Get raw cell value
            if excel_col not in df.columns:
                if field.is_required:
                    row_errors.append(RowError(
                        row_index=header_offset + row_idx + 2,  # actual 1-indexed row in the original file
                        column=excel_col,
                        message=f"Required column '{excel_col}' not found in file."
                    ))
                continue

            raw = row.get(excel_col)

            # Coerce
            try:
                coerced = _coerce_value(raw, field.data_type)
            except ValueError as e:
                row_errors.append(RowError(
                    row_index=header_offset + row_idx + 2,
                    column=excel_col,
                    message=str(e)
                ))
                continue

            # Required check
            if field.is_required and coerced is None:
                row_errors.append(RowError(
                    row_index=header_offset + row_idx + 2,
                    column=excel_col,
                    message=f"Required field '{field_name}' is missing or empty."
                ))
                continue

            # Resolving Foreign Key dynamically if specified
            if field.is_foreign_key and field.reference_table and field.reference_field:
                from services.normalization_service import get_or_create_fk
                try:
                    fk_id = get_or_create_fk(
                        db=db,
                        reference_table=field.reference_table,
                        reference_field=field.reference_field,
                        value=coerced
                    )
                    # Use the target_column (e.g. 'department_id') instead of the display field
                    final_key = field.target_column or field.field_name
                    row_data[final_key] = fk_id
                except Exception as e:
                    row_errors.append(RowError(
                        row_index=header_offset + row_idx + 2,
                        column=excel_col,
                        message=f"Foreign Key Resolution Error: {e}"
                    ))
                    continue
            else:
                row_data[field.field_name] = coerced

        # Check all required fields are satisfied
        for field in fields:
            final_key = field.target_column or field.field_name
            if field.is_required and final_key not in row_data:
                # Only add error if not already recorded for this field/col
                already = any(e.message.find(field.field_name) >= 0 for e in row_errors)
                if not already:
                    row_errors.append(RowError(
                        row_index=header_offset + row_idx + 2,
                        column=field.field_name,
                        message=f"Required field '{field.field_name}' has no mapping."
                    ))

        if row_errors:
            errors.extend(row_errors)
        else:
            valid_rows.append({"row_index": header_offset + row_idx + 2, "data": row_data})

    return valid_rows, errors


# ─────────────────────────────────────────────────
# 4. Full Ingest Orchestration
# ─────────────────────────────────────────────────

def ingest_data(
    session_id: int,
    schema_id: int,
    mapping: Dict[str, str],
    current_user: dict,
    db: Session,
    duplicate_mode: str = "skip"
) -> IngestResult:
    """
    Orchestrates the full ingest pipeline:
      file → transform → validate → bulk insert → audit log
    """
    # Load session
    session = db.query(UploadSession).filter(UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Upload session {session_id} not found.")
    if session.schema_id != schema_id:
        raise HTTPException(status_code=400, detail="Session schema_id does not match provided schema_id.")
    if session.status == "ingested":
        raise HTTPException(status_code=409, detail="This upload session has already been ingested.")

    # Load schema fields
    schema = db.query(DataSchema).filter(DataSchema.id == schema_id).first()
    fields = db.query(SchemaField).filter(SchemaField.schema_id == schema_id).all()
    if not fields:
        raise HTTPException(status_code=400, detail="Schema has no fields defined.")

    # Validate and transform
    valid_rows, errors = validate_and_transform(db, session.temp_file_path, mapping, fields)

    rows_skipped = len(errors)
    rows_inserted = 0
    rows_updated = 0
    duplicates_found = 0

    # Build field_name → field_id lookup for ColumnMapping records
    field_name_to_id: Dict[str, int] = {f.field_name: f.id for f in fields}

    # Bulk insert valid rows
    from services.normalization_service import perform_relational_upsert

    try:
        # Prevent persisting mapping early if we are just previewing
        if duplicate_mode != "preview":
            for excel_col, field_name in mapping.items():
                field_id = field_name_to_id.get(field_name)
                if field_id:
                    db.add(ColumnMapping(
                        session_id=session_id, excel_column=excel_col, field_id=field_id
                    ))

        for item in valid_rows:
            op_result = "inserted"
            if schema.target_table:
                try:
                    op_result = perform_relational_upsert(db, schema.target_table, item["data"], duplicate_mode)
                except ValueError as ve:
                    db.rollback()
                    raise HTTPException(status_code=409, detail=str(ve))
                    
            if op_result == "duplicate":
                duplicates_found += 1
            elif op_result == "updated":
                rows_updated += 1
                duplicates_found += 1
            elif op_result == "skipped":
                duplicates_found += 1
            elif op_result in ("inserted", "new"):
                rows_inserted += 1
                
            # Keep Audit trail JSON blob if we actually persisted the row
            if duplicate_mode != "preview" and op_result in ("inserted", "updated"):
                record = UploadedData(
                    schema_id=schema_id, session_id=session_id,
                    row_index=item["row_index"], data=json.dumps(item["data"], default=str),
                )
                db.add(record)

        if duplicate_mode == "preview":
            db.rollback()
            return IngestResult(
                rows_inserted=rows_inserted,
                rows_updated=0,
                rows_skipped=rows_skipped,
                duplicates_found=duplicates_found,
                errors=errors,
                warnings=["Preview mode - no data saved to database."],
                audit_log_id=None,
            )

        # Transaction safety guarantees everything above commits or nothing does.
        # Errors trigger exceptions bubbling up, breaking the commit.
        session.status = "ingested" if (rows_inserted + rows_updated) > 0 else "failed"
        session.detected_columns = json.dumps(list(mapping.keys()))

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Insertion Failed: {str(e)}")

    # Audit log
    user_id = current_user.get("user_id")
    user_email = current_user.get("sub", "unknown")
    audit = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action="UPLOAD",
        entity_type="uploaded_data",
        entity_id=schema_id,
        old_value=None,
        new_value=json.dumps({
            "session_id": session_id,
            "mapping": mapping,
            "rows_inserted": rows_inserted,
            "rows_updated": rows_updated,
            "duplicates": duplicates_found,
        }),
        timestamp=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    warnings: List[str] = []
    if rows_skipped > 0:
        warnings.append(f"{rows_skipped} row(s) were skipped due to validation errors.")
    if duplicates_found > 0:
        warnings.append(f"Handled {duplicates_found} duplicate records via '{duplicate_mode}' mode.")

    return IngestResult(
        rows_inserted=rows_inserted,
        rows_updated=rows_updated,
        rows_skipped=rows_skipped,
        duplicates_found=duplicates_found,
        errors=errors,
        warnings=warnings,
        audit_log_id=audit.id,
    )
