import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Table, MetaData, insert, select
from datetime import datetime

logger = logging.getLogger(__name__)

def get_or_create_fk(
    db: Session,
    reference_table: str,
    reference_field: str,
    value: Any
) -> Optional[int]:
    """
    Look up a value in a reference table, return its primary key ID.
    If it doesn't exist, create it and return the new ID.
    """
    if value is None or str(value).strip() == "":
        return None
        
    val_str = str(value).strip()
    
    # Use SQLAlchemy Core table reflection to interact with generic tables securely
    metadata = MetaData()
    table = Table(reference_table, metadata, autoload_with=db.bind)
    
    # Check if exists
    stmt = select(table.c.id).where(getattr(table.c, reference_field) == val_str)
    result = db.execute(stmt).scalar()
    
    if result is not None:
        return result
        
    # Insert new
    insert_stmt = insert(table).values({reference_field: val_str})
    insert_result = db.execute(insert_stmt)
    return insert_result.inserted_primary_key[0]


def perform_relational_upsert(
    db: Session,
    target_table: str,
    normalized_row: Dict[str, Any],
    mode: str = "skip"
) -> str:
    """
    Insert or Update a normalized dictionary into the specified relational table safely.
    Mode can be "skip", "update", "error", or "preview".
    Returns: "inserted", "updated", "skipped", "error", "duplicate", or "new"
    """
    metadata = MetaData()
    table = Table(target_table, metadata, autoload_with=db.bind)
    
    valid_cols = set(table.columns.keys())
    row_to_insert = {k: v for k, v in normalized_row.items() if k in valid_cols}

    # Identify primary/unique key matches
    # For MVP, we inspect table indexes or hardcode known domain constraints
    unique_keys = []
    if target_table == "students" and "student_id" in row_to_insert:
        unique_keys = ["student_id"]
    else:
        for c in table.columns:
            if (c.unique or c.primary_key) and c.name in row_to_insert:
                unique_keys.append(c.name)
                
    existing_row = None
    if unique_keys:
        stmt = select(table)
        for uk in unique_keys:
            stmt = stmt.where(getattr(table.c, uk) == row_to_insert[uk])
        existing_row = db.execute(stmt).first()
        
    if existing_row:
        if mode == "preview":
            return "duplicate"
        if mode == "error":
            raise ValueError(f"Duplicate record found for unique keys: {unique_keys}")
        if mode == "skip":
            return "skipped"
            
        # mode == "update"
        update_data = {}
        for k, v in row_to_insert.items():
            if k in unique_keys or k == "id":
                continue  # Never overwrite identity columns
            
            # Derived field protection: don't overwrite if existing value is present, except in intentional Update mode
            existing_val = getattr(existing_row, k, None)
            
            # Allow emails to be strictly overwritten if the user chose the Replace/Update mode
            # Previously this was locked to only overwrite placeholder.com emails
            update_data[k] = v
        if "updated_at" in valid_cols:
            update_data["updated_at"] = datetime.utcnow()
            
        if update_data:
            upd_stmt = table.update().where(table.c.id == existing_row.id).values(update_data)
            db.execute(upd_stmt)
            return "updated"
        return "skipped"
            
    # Not existing -> Insert
    if mode == "preview":
        return "new"
        
    # Add auto-timestamps if they exist randomly in target tables
    if "created_at" in valid_cols and "created_at" not in row_to_insert:
        row_to_insert["created_at"] = datetime.utcnow()
    if "updated_at" in valid_cols and "updated_at" not in row_to_insert:
        row_to_insert["updated_at"] = datetime.utcnow()
        
    # Domain-specific fallback hook for required DB constraints
    if target_table == "students":
        if "email" in valid_cols and "email" not in row_to_insert:
            s_id = row_to_insert.get("student_id", "unknown")
            row_to_insert["email"] = f"{s_id}@placeholder.com"
            
    ins_stmt = insert(table).values(row_to_insert)
    db.execute(ins_stmt)
    return "inserted"
