"""Test configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import Base, get_db
from database.models import User, Student
from auth.hashing import hash_password
from main import app

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_campus.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db):
    """Create a test admin user"""
    user = User(
        email="test_admin@campus.edu",
        hashed_password=hash_password("admin123"),
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_student_user(db):
    """Create a test student user"""
    user = User(
        email="test_student@campus.edu",
        hashed_password=hash_password("student123"),
        role="student"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_student_profile(db, test_student_user):
    """Create a test student profile"""
    student = Student(
        student_id="TEST2024001",
        name="Test Student",
        email="test_student@campus.edu",
        department="Computer Science",
        year=2,
        phone="+1234567890",
        address="123 Test Street"
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@pytest.fixture
def admin_token(client, test_admin_user):
    """Get JWT token for admin user"""
    response = client.post(
        "/auth/login",
        data={
            "username": "test_admin@campus.edu",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def student_token(client, test_student_user):
    """Get JWT token for student user"""
    response = client.post(
        "/auth/login",
        data={
            "username": "test_student@campus.edu",
            "password": "student123"
        }
    )
    return response.json()["access_token"]
