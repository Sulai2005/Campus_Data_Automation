"""
Generate sample student data for testing

This script creates realistic sample student records in the database.
You can specify the number of students to create.

Usage:
    python generate_sample_students.py [number_of_students]
    
Example:
    python generate_sample_students.py 50
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import Student


# Sample data for generating realistic student records
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy"
]

DEPARTMENTS = [
    "Computer Science",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Information Technology",
    "Electronics and Communication",
    "Chemical Engineering",
    "Biotechnology",
    "Mathematics",
    "Physics"
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
    "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington",
    "Boston", "Nashville", "Detroit", "Portland", "Las Vegas"
]

STREETS = [
    "Main Street", "Oak Avenue", "Maple Drive", "Cedar Lane", "Pine Road",
    "Elm Street", "Washington Avenue", "Park Place", "College Road", "University Drive",
    "Campus Way", "Academic Circle", "Scholar Lane", "Student Avenue", "Education Boulevard"
]


def generate_student_id(department, year, index):
    """Generate a unique student ID"""
    dept_code = {
        "Computer Science": "CS",
        "Electrical Engineering": "EE",
        "Mechanical Engineering": "ME",
        "Civil Engineering": "CE",
        "Information Technology": "IT",
        "Electronics and Communication": "EC",
        "Chemical Engineering": "CH",
        "Biotechnology": "BT",
        "Mathematics": "MA",
        "Physics": "PH"
    }
    
    code = dept_code.get(department, "XX")
    current_year = datetime.now().year
    return f"{code}{current_year}{index:03d}"


def generate_phone():
    """Generate a random phone number"""
    return f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"


def generate_address(city):
    """Generate a random address"""
    street_number = random.randint(100, 9999)
    street = random.choice(STREETS)
    return f"{street_number} {street}, {city}"


def generate_email(first_name, last_name):
    """Generate an email address"""
    return f"{first_name.lower()}.{last_name.lower()}@campus.edu"


def create_sample_students(count=10):
    """
    Create sample student records
    
    Args:
        count: Number of students to create (default: 10)
    """
    db = SessionLocal()
    
    try:
        print(f"Generating {count} sample students...")
        
        students = []
        existing_count = db.query(Student).count()
        
        for i in range(count):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            department = random.choice(DEPARTMENTS)
            year = random.randint(1, 4)
            city = random.choice(CITIES)
            
            student = Student(
                student_id=generate_student_id(department, year, existing_count + i + 1),
                name=f"{first_name} {last_name}",
                email=generate_email(first_name, last_name),
                department=department,
                year=year,
                phone=generate_phone(),
                address=generate_address(city)
            )
            
            students.append(student)
        
        # Add all students to database
        db.add_all(students)
        db.commit()
        
        print(f"\n[OK] Successfully created {count} sample students!")
        print(f"\nTotal students in database: {db.query(Student).count()}")
        
        # Show first 5 as examples
        print("\nSample records created:")
        for student in students[:5]:
            print(f"  - {student.student_id}: {student.name} ({student.department}, Year {student.year})")
        
        if count > 5:
            print(f"  ... and {count - 5} more")
        
    except Exception as e:
        print(f"ERROR: Failed to create students: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Get count from command line argument or use default
    count = 10
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
            if count < 1 or count > 1000:
                print("ERROR: Count must be between 1 and 1000")
                sys.exit(1)
        except ValueError:
            print("ERROR: Please provide a valid number")
            print("Usage: python generate_sample_students.py [number]")
            sys.exit(1)
    
    create_sample_students(count)
