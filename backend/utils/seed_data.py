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
            print("To re-seed, delete the database file and run this script again.")
            return
        
        print("Seeding database...")
        
        # Create test users (Admin and Staff)
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
        ]
        
        # Student users data
        student_users_data = [
            ("student@campus.edu", "Test Student", "CS2024001", "Computer Science", 1, "+1234567890", "100 Campus Drive, University Town"),
            ("john.doe@campus.edu", "John Doe", "CS2024002", "Computer Science", 2, "+1234567891", "123 Academic Street, University Town"),
            ("jane.smith@campus.edu", "Jane Smith", "CS2024003", "Computer Science", 3, "+1234567892", "456 College Avenue, University Town"),
            ("alice.johnson@campus.edu", "Alice Johnson", "EE2024001", "Electrical Engineering", 1, "+1234567893", "789 Scholar Lane, University Town"),
            ("bob.williams@campus.edu", "Bob Williams", "ME2024001", "Mechanical Engineering", 4, "+1234567894", "321 Education Road, University Town"),
            ("charlie.brown@campus.edu", "Charlie Brown", "CS2024004", "Computer Science", 2, "+1234567895", "555 Student Plaza, University Town"),
            ("diana.prince@campus.edu", "Diana Prince", "IT2024001", "Information Technology", 3, "+1234567896", "777 Tech Boulevard, University Town"),
            ("edward.norton@campus.edu", "Edward Norton", "CE2024001", "Civil Engineering", 1, "+1234567897", "888 Builder Street, University Town"),
            ("fiona.gallagher@campus.edu", "Fiona Gallagher", "EE2024002", "Electrical Engineering", 2, "+1234567898", "999 Circuit Avenue, University Town"),
            ("george.martin@campus.edu", "George Martin", "ME2024002", "Mechanical Engineering", 3, "+1234567899", "111 Machine Road, University Town"),
            ("hannah.montana@campus.edu", "Hannah Montana", "CS2024005", "Computer Science", 4, "+1234567800", "222 Code Street, University Town"),
            ("ian.malcolm@campus.edu", "Ian Malcolm", "IT2024002", "Information Technology", 1, "+1234567801", "333 Data Drive, University Town"),
            ("julia.roberts@campus.edu", "Julia Roberts", "CE2024002", "Civil Engineering", 2, "+1234567802", "444 Structure Lane, University Town"),
            ("kevin.hart@campus.edu", "Kevin Hart", "EE2024003", "Electrical Engineering", 3, "+1234567803", "555 Voltage Avenue, University Town"),
            ("laura.palmer@campus.edu", "Laura Palmer", "ME2024003", "Mechanical Engineering", 4, "+1234567804", "666 Engine Boulevard, University Town"),
            ("michael.scott@campus.edu", "Michael Scott", "CS2024006", "Computer Science", 1, "+1234567805", "777 Algorithm Street, University Town"),
            ("nancy.drew@campus.edu", "Nancy Drew", "IT2024003", "Information Technology", 2, "+1234567806", "888 Network Road, University Town"),
            ("oliver.queen@campus.edu", "Oliver Queen", "CE2024003", "Civil Engineering", 3, "+1234567807", "999 Foundation Drive, University Town"),
            ("peter.parker@campus.edu", "Peter Parker", "EE2024004", "Electrical Engineering", 4, "+1234567808", "101 Power Lane, University Town"),
            ("quinn.fabray@campus.edu", "Quinn Fabray", "ME2024004", "Mechanical Engineering", 1, "+1234567809", "202 Gear Street, University Town"),
            ("rachel.green@campus.edu", "Rachel Green", "CS2024007", "Computer Science", 2, "+1234567810", "303 Binary Boulevard, University Town"),
            ("sam.winchester@campus.edu", "Sam Winchester", "IT2024004", "Information Technology", 3, "+1234567811", "404 Server Avenue, University Town"),
            ("tina.fey@campus.edu", "Tina Fey", "CE2024004", "Civil Engineering", 4, "+1234567812", "505 Concrete Road, University Town"),
            ("uma.thurman@campus.edu", "Uma Thurman", "EE2024005", "Electrical Engineering", 1, "+1234567813", "606 Current Street, University Town"),
            ("victor.stone@campus.edu", "Victor Stone", "ME2024005", "Mechanical Engineering", 2, "+1234567814", "707 Torque Lane, University Town"),
        ]
        
        # Create student users and student records
        students = []
        for email, name, student_id, department, year, phone, address in student_users_data:
            # Create user account
            user = User(
                email=email,
                hashed_password=hash_password("student123"),
                role="student"
            )
            users.append(user)
            
            # Create student record
            student = Student(
                student_id=student_id,
                name=name,
                email=email,
                department=department,
                year=year,
                phone=phone,
                address=address
            )
            students.append(student)
        
        # Add all users
        db.add_all(users)
        db.commit()
        print(f"[OK] Created {len(users)} user accounts")
        
        # Add all students
        db.add_all(students)
        db.commit()
        print(f"[OK] Created {len(students)} student records")
        
        print("\n" + "="*60)
        print("SUCCESS: Database seeded successfully!")
        print("="*60)
        print("\nTest Credentials:")
        print("\n🔐 Admin Account:")
        print("  Email: admin@campus.edu")
        print("  Password: admin123")
        print("\n👨‍💼 Staff Account:")
        print("  Email: staff@campus.edu")
        print("  Password: staff123")
        print(f"\n👨‍🎓 Student Accounts ({len(student_users_data)} total - all use password: student123):")
        print("  Sample accounts:")
        for i, (email, name, _, dept, year, _, _) in enumerate(student_users_data[:5]):
            print(f"  • {email} ({name} - {dept}, Year {year})")
        print(f"  ... and {len(student_users_data) - 5} more student accounts")
        print("\n📊 Database Statistics:")
        print(f"  Total Users: {len(users)}")
        print(f"  Admin/Staff: 2")
        print(f"  Students: {len(students)}")
        print(f"  Departments: Computer Science, Electrical Engineering, Mechanical Engineering,")
        print(f"               Civil Engineering, Information Technology")
        print("="*60)
        
    except Exception as e:
        print(f"ERROR: Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
