# 🚀 Quick Start Guide

## Module-1 Prototype: Authentication & RBAC

This guide will help you get the Campus Data Workflow Automation System up and running in minutes.

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

---

## Installation Steps

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI
- SQLAlchemy
- JWT authentication libraries
- Testing tools
- All other required packages

### 3. Seed the Database

Create test users and sample student data:

```bash
python -m utils.seed_data
```

This creates:
- **Admin user**: `admin@campus.edu` / `admin123`
- **Staff user**: `staff@campus.edu` / `staff123`
- **Student user**: `student@campus.edu` / `student123`
- Sample student profiles

**Optional:** Generate additional sample students:
```bash
python -m utils.generate_sample_students 50
```
This creates realistic sample student data for testing reports.

### 4. Start the Backend Server

```bash
uvicorn main:app --reload
```

The server will start at: `http://127.0.0.1:8000`

---

## Testing the System

### Option 1: Web Interface (Recommended)

1. **Open your browser and navigate to:**
   ```
   http://127.0.0.1:8000
   ```
   
   The login page will load automatically.

2. **Login as Admin:**
   - Email: `admin@campus.edu`
   - Password: `admin123`
   - You'll be redirected to the admin dashboard

3. **Test Admin Features:**
   - Navigate to **Upload** page
   - Upload a test file (JPG, PNG, or PDF)
   - Navigate to **Reports** page
   - Generate a student report with filters

4. **Login as Student:**
   - Logout from admin
   - Email: `student@campus.edu`
   - Password: `student123`
   - View read-only student dashboard

### Option 2: API Documentation

Visit the auto-generated API docs:
```
http://127.0.0.1:8000/docs
```

Test endpoints directly in the Swagger UI.

### Option 3: Run Automated Tests

```bash
cd backend
pytest tests/ -v
```

All tests should pass ✅

---

## Test Credentials

### Admin Account
- **Email:** admin@campus.edu
- **Password:** admin123
- **Access:** All admin pages (dashboard, upload, reports)

### Staff Account
- **Email:** staff@campus.edu
- **Password:** staff123
- **Access:** Same as admin (for Module-1)

### Student Accounts
- **Email:** student@campus.edu
- **Password:** student123
- **Access:** Student dashboard (read-only)

- **Email:** john.doe@campus.edu
- **Password:** student123
- **Student ID:** CS2024001

- **Email:** jane.smith@campus.edu
- **Password:** student123
- **Student ID:** CS2024002

---

## Project Structure

```
Campus_Data_Automation/
│
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── database/
│   │   ├── db.py                  # Database connection
│   │   └── models.py              # SQLAlchemy models
│   ├── auth/
│   │   ├── hashing.py             # Password utilities
│   │   ├── jwt.py                 # JWT token generation
│   │   └── dependencies.py        # RBAC guards
│   ├── routers/
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── admin.py               # Admin endpoints
│   │   ├── students.py            # Student endpoints
│   │   └── reports.py             # Reports endpoints (NEW)
│   ├── reports/                   # Reports module (NEW)
│   │   ├── __init__.py
│   │   └── student_basic_report.py
│   ├── services/
│   │   ├── upload_service.py      # File upload logic
│   │   └── report_service.py      # Report generation
│   ├── utils/
│   │   ├── seed_data.py           # Database seeding
│   │   └── generate_sample_students.py  # Sample data generator (NEW)
│   └── tests/
│       ├── conftest.py            # Test configuration
│       ├── test_auth.py           # Auth tests
│       ├── test_rbac.py           # RBAC tests
│       └── test_upload.py         # Upload tests
│
└── frontend/
    ├── public/
    │   ├── login.html             # Login page
    │   ├── admin/
    │   │   ├── dashboard.html     # Admin dashboard
    │   │   ├── upload.html        # File upload page
    │   │   └── reports.html       # Reports page
    │   └── student/
    │       └── dashboard.html     # Student dashboard
    ├── styles/
    │   └── main.css               # Shared styles
    └── scripts/
        └── auth.js                # Auth utilities
```

---

## Common Issues & Solutions

### Issue: Module not found errors

**Solution:** Make sure you're in the `backend` directory when running commands:
```bash
cd backend
python -m utils.seed_data
```

### Issue: Port 8000 already in use

**Solution:** Kill the existing process or use a different port:
```bash
uvicorn main:app --reload --port 8001
```

Then update `API_BASE_URL` in frontend files to `http://127.0.0.1:8001`

### Issue: CORS errors in browser

**Solution:** The backend already has CORS enabled. Make sure:
1. Backend is running
2. You're accessing frontend files via `file://` protocol
3. Browser console shows the correct API URL

### Issue: Login fails with 401

**Solution:** 
1. Ensure database is seeded: `python -m utils.seed_data`
2. Check credentials are correct
3. Check backend logs for errors

### Issue: Student dashboard shows "Profile not found"

**Solution:** The student user must have a corresponding entry in the `students` table with matching email. The seed script creates this automatically.

---

## API Endpoints

### Authentication
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Admin (Requires admin role)
- `GET /admin/dashboard` - Dashboard data
- `POST /admin/upload/file` - Upload file
- `POST /admin/reports/generate` - Generate report

### Student (Requires student role)
- `GET /student/dashboard` - Student dashboard
- `GET /student/profile` - Detailed profile

### Reports (Requires admin role)
- `GET /reports/student-basic` - Generate student basic report
- `GET /reports/available` - List available reports

### Public
- `GET /` - API status
- `GET /health` - Health check
- `GET /docs` - API documentation

---

## Next Steps

After successfully running Module-1:

1. **Explore the Code:** Review the modular architecture
2. **Run Tests:** Ensure all tests pass
3. **Customize:** Modify CSS, add fields, etc.
4. **Module-2:** Implement enhanced student features
5. **Module-3:** Add update request workflow

---

## Getting Help

- Check `README.md` for architecture details
- Review `PLAN.md` for module roadmap
- See `MODULIZATION.md` for auth implementation details
- Check `implementation_plan.md` for detailed design decisions

---

## Success Criteria ✅

You've successfully set up Module-1 if:

- ✅ Backend starts without errors
- ✅ Database is created and seeded
- ✅ You can login as admin
- ✅ You can login as student
- ✅ Admin can upload files
- ✅ Admin can generate reports
- ✅ Student sees read-only dashboard
- ✅ All tests pass

**Congratulations! You're ready to build Module-2! 🎉**
