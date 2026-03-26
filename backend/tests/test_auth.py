"""Authentication tests"""

import pytest


def test_login_success(client, test_admin_user):
    """Test successful login with valid credentials"""
    response = client.post(
        "/auth/login",
        data={
            "username": "test_admin@campus.edu",
            "password": "admin123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "admin"


def test_login_invalid_email(client, test_admin_user):
    """Test login with invalid email"""
    response = client.post(
        "/auth/login",
        data={
            "username": "wrong@campus.edu",
            "password": "admin123"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_invalid_password(client, test_admin_user):
    """Test login with invalid password"""
    response = client.post(
        "/auth/login",
        data={
            "username": "test_admin@campus.edu",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_get_current_user(client, admin_token):
    """Test getting current user info with valid token"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_admin@campus.edu"
    assert data["role"] == "admin"


def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get("/auth/me")
    
    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]
