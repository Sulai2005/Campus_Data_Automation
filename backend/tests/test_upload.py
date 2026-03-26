"""File upload tests"""

import pytest
import io


def test_upload_file_success(client, admin_token, test_student_profile):
    """Test successful file upload"""
    # Create a fake file
    file_content = b"fake image content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/admin/upload/file",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("test_photo.jpg", file, "image/jpeg")},
        data={
            "student_id": test_student_profile.id,
            "file_type": "photo"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File uploaded successfully"
    assert "file_info" in data


def test_upload_file_invalid_student(client, admin_token):
    """Test file upload with invalid student ID"""
    file_content = b"fake image content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/admin/upload/file",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("test_photo.jpg", file, "image/jpeg")},
        data={
            "student_id": 99999,  # Non-existent student
            "file_type": "photo"
        }
    )
    
    assert response.status_code == 404
    assert "Student not found" in response.json()["detail"]


def test_upload_file_invalid_extension(client, admin_token, test_student_profile):
    """Test file upload with invalid file extension"""
    file_content = b"fake executable content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/admin/upload/file",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("malware.exe", file, "application/x-msdownload")},
        data={
            "student_id": test_student_profile.id,
            "file_type": "photo"
        }
    )
    
    assert response.status_code == 400
    assert "File type not allowed" in response.json()["detail"]


def test_upload_file_student_cannot_upload(client, student_token, test_student_profile):
    """Test that students cannot upload files"""
    file_content = b"fake image content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/admin/upload/file",
        headers={"Authorization": f"Bearer {student_token}"},
        files={"file": ("test_photo.jpg", file, "image/jpeg")},
        data={
            "student_id": test_student_profile.id,
            "file_type": "photo"
        }
    )
    
    assert response.status_code == 403
