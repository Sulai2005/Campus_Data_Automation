import os
import sys

# Ensure backend directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import engine, Base, SessionLocal
from database.models import User, DataSchema, SchemaField
from auth.hashing import Hash

def init_admin_and_schema():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create Admin
        admin_email = "admin@example.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                hashed_password=Hash.bcrypt("admin123"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            print(f"Created admin user: {admin_email} / admin123")
        else:
            print("Admin user already exists.")
            
        # Ensure Core Student Schema is created
        schema = db.query(DataSchema).filter(DataSchema.name == 'Core Student Database').first()
        if not schema:
            schema = DataSchema(
                name='Core Student Database',
                description='Core database ingestion schema for inserting directly into the students table.',
                target_table='students'
            )
            db.add(schema)
            db.commit()
            db.refresh(schema)
            
            # Add fields with normalization mappings
            fields = [
                SchemaField(schema_id=schema.id, field_name='student_id', data_type='string', is_required=True),
                SchemaField(schema_id=schema.id, field_name='name', data_type='string', is_required=True),
                # Normalized department lookup
                SchemaField(
                    schema_id=schema.id, field_name='department', data_type='string', is_required=True,
                    is_foreign_key=True, reference_table='departments', reference_field='name', target_column='department_id'
                ),
            ]
            db.bulk_save_objects(fields)
            db.commit()
            print("Created Core Student Database Schema.")
        else:
            print("Core Student Database Schema already exists.")
            
    except Exception as e:
        print(f"Error initializing system: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_admin_and_schema()
