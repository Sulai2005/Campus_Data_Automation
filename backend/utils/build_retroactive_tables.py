import sys
import os
import re
from datetime import datetime

# Add the backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import SessionLocal
from database.models import DataSchema, SchemaField
from sqlalchemy import Table, MetaData, Column, Integer, String, Float, Date, text

def run():
    db = SessionLocal()
    
    # Find all schemas that do strictly generic JSON data-laking (target_table=None)
    orphan_schemas = db.query(DataSchema).filter(DataSchema.target_table == None).all()
    
    if not orphan_schemas:
        print("No retroactive tables needed. Everything is mapped.")
        db.close()
        return

    print(f"Found {len(orphan_schemas)} orphan schemas to convert to physical SQL tables...")
    
    for schema in orphan_schemas:
        print(f"-> Processing Schema: {schema.name}")
        safe_name = "dynamic_" + re.sub(r'[^a-zA-Z0-9]', '_', schema.name.lower())
        
        metadata = MetaData()
        columns = [
            Column('id', Integer, primary_key=True, autoincrement=True),
        ]
        
        fields = db.query(SchemaField).filter(SchemaField.schema_id == schema.id).all()
        
        for field in fields:
            # Map UI fields to SQL table columns
            safe_col_name = re.sub(r'[^a-zA-Z0-9]', '_', field.field_name.lower())
            
            col_type = String
            if field.data_type == 'int':
                col_type = Integer
            elif field.data_type == 'float':
                col_type = Float
            elif field.data_type == 'date':
                col_type = Date
                
            columns.append(Column(safe_col_name, col_type, nullable=not field.is_required))
            
            # Update the schema field targeting rules
            field.target_column = safe_col_name
            db.add(field)

        columns.append(Column('created_at', String, default=lambda: datetime.utcnow().isoformat()))
        columns.append(Column('updated_at', String, default=lambda: datetime.utcnow().isoformat()))
        
        dynamic_table = Table(safe_name, metadata, *columns)
        
        try:
            dynamic_table.create(bind=db.get_bind())
            print(f"   [SUCCESS] Created table '{safe_name}'")
        except Exception as e:
            print(f"   [WARNING] Table creation failed (might already exist): {e}")
            
        # Bind the schema routing strictly to this new table
        schema.target_table = safe_name
        db.add(schema)
        
    db.commit()
    db.close()
    print("Retroactive building complete.")

if __name__ == "__main__":
    run()
