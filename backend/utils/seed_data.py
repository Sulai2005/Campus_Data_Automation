"""Seed database with test users and sample data"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal, engine
from database.models import Base, User, Student
from auth.hashing import hash_password


def seed_database():
    """Create test users and sample student data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("WARNING: Database already contains users. Skipping seed.")
            return
        
        print("Seeding database...")
        
        # Create test users
        users = [
            User(
                email="admin@campus.edu",
                hashed_password=hash_password("admin123"),
                role="admin"
            ),
            User(
                email="staff@campus.edu",
                hashed_password=hash_password("staff123"),
                role="staff"
            ),
            User(
                email="student@campus.edu",
                hashed_password=hash_password("student123"),
                role="student"
            ),
            User(
                email="john.doe@campus.edu",
                hashed_password=hash_password("student123"),
                role="student"
            ),
            User(
                email="jane.smith@campus.edu",
                hashed_password=hash_password("student123"),
                role="student"
            )
        ]
        
        db.add_all(users)
        db.commit()
        print("[OK] Created test users")
        
        # Create sample students
        students = [
            Student(
                student_id="CS2024001",
                name="John Doe",
                email="john.doe@campus.edu",
                department="Computer Science",
                year=2,
                phone="+1234567890",
                address="123 Campus Street, University Town"
            ),
            Student(
                student_id="CS2024002",
                name="Jane Smith",
                email="jane.smith@campus.edu",
                department="Computer Science",
                year=3,
                phone="+1234567891",
                address="456 College Avenue, University Town"
            ),
            Student(
                student_id="EE2024001",
                name="Alice Johnson",
                email="alice.johnson@campus.edu",
                department="Electrical Engineering",
                year=1,
                phone="+1234567892",
                address="789 Academic Road, University Town"
            ),
            Student(
                student_id="ME2024001",
                name="Bob Williams",
                email="bob.williams@campus.edu",
                department="Mechanical Engineering",
                year=4,
                phone="+1234567893",
                address="321 Scholar Lane, University Town"
            )
        ]
        
        db.add_all(students)
        db.commit()
        print("[OK] Created sample students")
        
        print("\n" + "="*60)
        print("SUCCESS: Database seeded successfully!")
        print("="*60)
        print("\nTest Credentials:")
        print("\nAdmin:")
        print("  Email: admin@campus.edu")
        print("  Password: admin123")
        print("\nStaff:")
        print("  Email: staff@campus.edu")
        print("  Password: staff123")
        print("\nStudent:")
        print("  Email: student@campus.edu")
        print("  Password: student123")
        print("\nOther Students:")
        print("  Email: john.doe@campus.edu")
        print("  Password: student123")
        print("  Email: jane.smith@campus.edu")
        print("  Password: student123")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"ERROR: Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
