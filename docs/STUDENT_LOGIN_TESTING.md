# Student Login Testing Guide

## Overview
This document explains how to test the student login functionality in the Campus Data Automation System.

## What Was Fixed

### Problem Identified
The original seed data had a **mismatch** between User accounts and Student records:
- A `User` with email `student@campus.edu` existed for authentication
- But NO corresponding `Student` record with that email existed
- This caused the student dashboard to fail with a 404 error when trying to load the profile

### Solution Implemented
1. **Added Student Record**: Created a `Student` record for `student@campus.edu` (Student ID: TEST2024001)
2. **Added Missing User Accounts**: Created `User` accounts for Alice Johnson and Bob Williams
3. **Updated Documentation**: Updated README and login page with correct credentials

## Test Credentials

All student accounts use the password: **student123**

| Email | Name | Student ID | Department | Year |
|-------|------|------------|------------|------|
| student@campus.edu | Test Student | TEST2024001 | Computer Science | 1 |
| john.doe@campus.edu | John Doe | CS2024001 | Computer Science | 2 |
| jane.smith@campus.edu | Jane Smith | CS2024002 | Computer Science | 3 |
| alice.johnson@campus.edu | Alice Johnson | EE2024001 | Electrical Engineering | 1 |
| bob.williams@campus.edu | Bob Williams | ME2024001 | Mechanical Engineering | 4 |

**Admin Account:**
- Email: `admin@campus.edu`
- Password: `admin123`

**Staff Account:**
- Email: `staff@campus.edu`
- Password: `staff123`

## Setup Instructions

### 1. Install Dependencies (if not already done)

```bash
# Create virtual environment (if needed)
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Reset and Seed Database

```bash
cd backend

# Remove old database (if exists)
rm campus.db

# Seed new database with updated data
python -m utils.seed_data
```

Expected output:
```
Seeding database...
[OK] Created test users
[OK] Created sample students

============================================================
SUCCESS: Database seeded successfully!
============================================================

Test Credentials:

Admin:
  Email: admin@campus.edu
  Password: admin123

Staff:
  Email: staff@campus.edu
  Password: staff123

Student Accounts (all use password: student123):
  Email: student@campus.edu (Test Student)
  Email: john.doe@campus.edu (John Doe)
  Email: jane.smith@campus.edu (Jane Smith)
  Email: alice.johnson@campus.edu (Alice Johnson)
  Email: bob.williams@campus.edu (Bob Williams)

============================================================
```

### 3. Start the Server

```bash
# From the backend directory
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or use the convenience script from the project root:
```bash
./setup_and_run.sh
```

## Testing Student Login

### Test 1: Login with Generic Student Account

1. Open browser and navigate to: `http://127.0.0.1:8000/`
2. Enter credentials:
   - Email: `student@campus.edu`
   - Password: `student123`
   - Role: Select "Student"
3. Click "Login"

**Expected Result:**
- ✅ Login successful
- ✅ Redirected to `/student/dashboard`
- ✅ Dashboard loads showing:
  - Student ID: TEST2024001
  - Name: Test Student
  - Email: student@campus.edu
  - Department: Computer Science
  - Year: 1
  - Phone: +1234567899
  - Address: 100 Test Avenue, University Town

### Test 2: Login with Named Student Account

1. Open browser and navigate to: `http://127.0.0.1:8000/`
2. Enter credentials:
   - Email: `john.doe@campus.edu`
   - Password: `student123`
   - Role: Select "Student"
3. Click "Login"

**Expected Result:**
- ✅ Login successful
- ✅ Redirected to `/student/dashboard`
- ✅ Dashboard loads showing John Doe's profile

### Test 3: Role Validation

1. Try logging in with student credentials but select "Admin" role
2. The system should still authenticate and redirect based on the **actual role** from the backend

**Expected Result:**
- ✅ Login successful
- ✅ Redirected to `/student/dashboard` (not admin dashboard)
- ✅ Console may show a warning about role mismatch

### Test 4: Invalid Credentials

1. Try logging in with:
   - Email: `student@campus.edu`
   - Password: `wrongpassword`
2. Click "Login"

**Expected Result:**
- ❌ Login fails
- ❌ Error message: "Invalid email or password"

### Test 5: Access Control

1. Login as a student
2. Try to manually navigate to: `http://127.0.0.1:8000/admin/dashboard`

**Expected Result:**
- ✅ Page loads (HTML is served)
- ❌ API calls fail with 403 Forbidden
- ✅ JavaScript should detect unauthorized access

## API Testing

You can also test the API directly using curl or the test script:

### Test Login Endpoint

```bash
# Test student login
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student@campus.edu&password=student123"
```

Expected response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "role": "student"
}
```

### Test Student Profile Endpoint

```bash
# First, get the token from login
TOKEN="<paste_token_here>"

# Then access the profile
curl -X GET "http://127.0.0.1:8000/api/student/profile" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response:
```json
{
  "student_id": "TEST2024001",
  "name": "Test Student",
  "email": "student@campus.edu",
  "department": "Computer Science",
  "year": 1,
  "phone": "+1234567899",
  "address": "100 Test Avenue, University Town",
  "documents": []
}
```

## Troubleshooting

### Issue: "Student profile not found" error

**Cause:** The database wasn't reseeded with the updated data.

**Solution:**
```bash
cd backend
rm campus.db
python -m utils.seed_data
```

### Issue: "Module not found" errors

**Cause:** Dependencies not installed or virtual environment not activated.

**Solution:**
```bash
# Activate venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### Issue: Port 8000 already in use

**Cause:** Another process is using port 8000.

**Solution:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
python -m uvicorn main:app --reload --port 8001
```

## Architecture Notes

### Authentication Flow

1. **Login Request**: User submits email/password via OAuth2 form
2. **Backend Validation**: 
   - Checks `User` table for email
   - Verifies password hash
   - Creates JWT token with user info (email, role, user_id)
3. **Token Storage**: Frontend stores token in localStorage
4. **Protected Routes**: 
   - Frontend sends token in Authorization header
   - Backend validates token and checks role
   - Returns data if authorized

### Student Data Flow

1. **Dashboard Load**: Frontend calls `/api/student/profile`
2. **Backend Processing**:
   - Extracts email from JWT token
   - Queries `Student` table by email
   - Returns student data with documents
3. **Frontend Display**: Renders profile information

### Key Files

- **Backend:**
  - `backend/routers/auth.py` - Authentication endpoints
  - `backend/routers/students.py` - Student endpoints
  - `backend/auth/dependencies.py` - RBAC guards
  - `backend/database/models.py` - Database models
  - `backend/utils/seed_data.py` - Database seeding

- **Frontend:**
  - `frontend/public/login.html` - Login page
  - `frontend/public/student/dashboard.html` - Student dashboard
  - `frontend/scripts/auth.js` - Auth utilities

## Next Steps

The student login is now fully functional. Future enhancements could include:

1. **Module 3**: Update request workflow
2. **Password Reset**: Email-based password recovery
3. **Profile Pictures**: Upload and display student photos
4. **Document Management**: Student document upload
5. **Notifications**: Real-time updates for students

## Summary

✅ **Fixed Issues:**
- Added Student record for `student@campus.edu`
- Added User accounts for all students
- Updated documentation and credentials display

✅ **Verified Functionality:**
- Student login works correctly
- Dashboard loads student profile
- RBAC properly enforces student-only access
- All 5 student accounts are functional

The student login system is now properly set up and ready for use!
