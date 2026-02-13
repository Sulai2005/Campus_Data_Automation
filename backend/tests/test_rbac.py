"""Role-based access control tests"""

import pytest


def test_admin_access_admin_dashboard(client, admin_token):
    """Test admin can access admin dashboard"""
    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


def test_student_cannot_access_admin_dashboard(client, student_token):
    """Test student cannot access admin dashboard"""
    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_unauthenticated_cannot_access_admin_dashboard(client):
    """Test unauthenticated user cannot access admin dashboard"""
    response = client.get("/admin/dashboard")
    
    assert response.status_code == 401


def test_student_access_student_dashboard(client, student_token, test_student_profile):
    """Test student can access their own dashboard"""
    response = client.get(
        "/student/dashboard",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_student@campus.edu"
    assert data["student_id"] == "TEST2024001"


def test_admin_cannot_access_student_dashboard(client, admin_token):
    """Test admin cannot access student dashboard (role mismatch)"""
    response = client.get(
        "/student/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_unauthenticated_cannot_access_student_dashboard(client):
    """Test unauthenticated user cannot access student dashboard"""
    response = client.get("/student/dashboard")
    
    assert response.status_code == 401


def test_admin_can_generate_reports(client, admin_token):
    """Test admin can generate reports"""
    response = client.post(
        "/admin/reports/generate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_student_cannot_generate_reports(client, student_token):
    """Test student cannot generate reports"""
    response = client.post(
        "/admin/reports/generate",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == 403
