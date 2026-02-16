# Student Login Architecture - Complete Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │ login.html   │      │ student/     │      │ admin/       │  │
│  │              │─────▶│ dashboard    │      │ dashboard    │  │
│  │ - Email      │      │              │      │              │  │
│  │ - Password   │      │ - Profile    │      │ - Upload     │  │
│  │ - Role       │      │ - Documents  │      │ - Reports    │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                      │                      │          │
│         │                      │                      │          │
│         └──────────────────────┼──────────────────────┘          │
│                                │                                 │
│                    ┌───────────▼───────────┐                    │
│                    │   scripts/auth.js     │                    │
│                    │                       │                    │
│                    │ - getToken()          │                    │
│                    │ - apiRequest()        │                    │
│                    │ - requireRole()       │                    │
│                    └───────────┬───────────┘                    │
└────────────────────────────────┼────────────────────────────────┘
                                 │
                                 │ HTTP Requests
                                 │ Authorization: Bearer <token>
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                         BACKEND (FastAPI)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    main.py (Entry Point)                  │  │
│  │                                                            │  │
│  │  - CORS Middleware                                        │  │
│  │  - Static File Serving                                    │  │
│  │  - Router Registration                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ routers/     │  │ routers/     │  │ routers/     │          │
│  │ auth.py      │  │ students.py  │  │ admin.py     │          │
│  │              │  │              │  │              │          │
│  │ POST /login  │  │ GET /profile │  │ POST /upload │          │
│  │ GET  /me     │  │ GET /dash    │  │ GET  /dash   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         │                 │                  │                   │
│  ┌──────▼─────────────────▼──────────────────▼───────┐          │
│  │           auth/dependencies.py (RBAC)             │          │
│  │                                                    │          │
│  │  - get_current_user(token) → user_payload         │          │
│  │  - require_admin(user) → user or 403              │          │
│  │  - require_student(user) → user or 403            │          │
│  └────────────────────────┬───────────────────────────┘          │
│                           │                                      │
│  ┌────────────────────────▼───────────────────────┐             │
│  │         auth/jwt.py (Token Management)         │             │
│  │                                                 │             │
│  │  - create_access_token(payload) → JWT          │             │
│  │  - decode_token(token) → payload               │             │
│  └─────────────────────────────────────────────────┘             │
│                                                                   │
│  ┌─────────────────────────────────────────────────┐            │
│  │      database/models.py (ORM Models)            │            │
│  │                                                  │            │
│  │  ┌────────┐  ┌─────────┐  ┌──────────────┐    │            │
│  │  │ User   │  │ Student │  │ StudentDoc   │    │            │
│  │  │        │  │         │  │              │    │            │
│  │  │ email  │  │ email   │  │ student_id   │    │            │
│  │  │ pass   │  │ name    │  │ file_path    │    │            │
│  │  │ role   │  │ dept    │  │ file_type    │    │            │
│  │  └────────┘  └─────────┘  └──────────────┘    │            │
│  └─────────────────────────────────────────────────┘            │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                     DATABASE (SQLite)                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │  users           │  │  students        │                     │
│  ├──────────────────┤  ├──────────────────┤                     │
│  │ id (PK)          │  │ id (PK)          │                     │
│  │ email (UNIQUE)   │  │ student_id       │                     │
│  │ hashed_password  │  │ name             │                     │
│  │ role             │  │ email (UNIQUE)   │◀─┐                  │
│  │ created_at       │  │ department       │  │                  │
│  └──────────────────┘  │ year             │  │ Email Match      │
│                        │ phone            │  │ (Critical!)      │
│                        │ address          │  │                  │
│                        └──────────────────┘──┘                  │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ student_docs     │  │ audit_logs       │                     │
│  ├──────────────────┤  ├──────────────────┤                     │
│  │ id (PK)          │  │ id (PK)          │                     │
│  │ student_id (FK)  │  │ user_email       │                     │
│  │ file_type        │  │ action           │                     │
│  │ file_path        │  │ entity_type      │                     │
│  │ uploaded_at      │  │ timestamp        │                     │
│  └──────────────────┘  └──────────────────┘                     │
└──────────────────────────────────────────────────────────────────┘
```

## Authentication Flow (Step-by-Step)

### 1. Login Request
```
User enters:
  - Email: student@campus.edu
  - Password: student123
  - Role: student (UI only)

Frontend (login.html):
  ↓
  Creates FormData with username=email, password=password
  ↓
  POST /api/auth/login
```

### 2. Backend Authentication
```
Backend (routers/auth.py):
  ↓
  Query User table: WHERE email = 'student@campus.edu'
  ↓
  Verify password: bcrypt.verify(password, user.hashed_password)
  ↓
  Create JWT token:
    {
      "sub": "student@campus.edu",
      "role": "student",
      "user_id": 3
    }
  ↓
  Return:
    {
      "access_token": "eyJhbGc...",
      "token_type": "bearer",
      "role": "student"
    }
```

### 3. Frontend Storage & Redirect
```
Frontend (login.html):
  ↓
  localStorage.setItem('token', access_token)
  localStorage.setItem('role', role)
  ↓
  if (role === 'student'):
    window.location.href = '/student/dashboard'
```

### 4. Dashboard Load
```
Frontend (student/dashboard.html):
  ↓
  requireRole('student')  // Checks localStorage
  ↓
  loadStudentProfile()
  ↓
  GET /api/student/profile
  Headers: { Authorization: "Bearer eyJhbGc..." }
```

### 5. Profile Data Retrieval
```
Backend (routers/students.py):
  ↓
  Dependency: require_student(token)
    ↓
    auth/dependencies.py:
      - Decode JWT token
      - Verify role === 'student'
      - Return user_payload
  ↓
  Query Student table: WHERE email = user_payload['sub']
  ↓
  Query StudentDocument table: WHERE student_id = student.id
  ↓
  Return JSON:
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

### 6. Frontend Display
```
Frontend (student/dashboard.html):
  ↓
  displayProfile(data)
  ↓
  Renders HTML with student information
```

## Critical Data Relationships

### The Email Link (MUST MATCH!)

```
┌─────────────────────┐         ┌─────────────────────┐
│  User Table         │         │  Student Table      │
├─────────────────────┤         ├─────────────────────┤
│ email (for login)   │ ═══════ │ email (for profile) │
│ hashed_password     │  MUST   │ name                │
│ role = 'student'    │  MATCH  │ student_id          │
└─────────────────────┘         └─────────────────────┘
```

**This was the bug!** 
- User `student@campus.edu` existed
- But NO Student with email `student@campus.edu` existed
- Login succeeded, but profile lookup failed → 404

**Fix:**
- Added Student record with email `student@campus.edu`

## Seed Data Structure

### Users Created
```python
users = [
    User(email="admin@campus.edu", role="admin"),
    User(email="staff@campus.edu", role="staff"),
    User(email="student@campus.edu", role="student"),      # ← Generic test account
    User(email="john.doe@campus.edu", role="student"),     # ← Named accounts
    User(email="jane.smith@campus.edu", role="student"),
    User(email="alice.johnson@campus.edu", role="student"),
    User(email="bob.williams@campus.edu", role="student"),
]
```

### Students Created (MUST MATCH User emails!)
```python
students = [
    Student(email="student@campus.edu", ...),         # ← ADDED (was missing!)
    Student(email="john.doe@campus.edu", ...),
    Student(email="jane.smith@campus.edu", ...),
    Student(email="alice.johnson@campus.edu", ...),   # ← User ADDED
    Student(email="bob.williams@campus.edu", ...),    # ← User ADDED
]
```

## Security Features

### 1. Password Hashing
```
Plain Password: "student123"
     ↓
bcrypt.hashpw(password, salt)
     ↓
Stored: "$2b$12$..."
```

### 2. JWT Token
```
Payload:
{
  "sub": "student@campus.edu",
  "role": "student",
  "user_id": 3,
  "exp": 1234567890
}
     ↓
jwt.encode(payload, SECRET_KEY, algorithm="HS256")
     ↓
Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Role-Based Access Control (RBAC)
```
@router.get("/profile")
def get_profile(
    current_user: dict = Depends(require_student)  # ← RBAC Guard
):
    # Only students can access this endpoint
    # Admin/Staff get 403 Forbidden
```

## File Structure

```
Campus_Data_Automation/
│
├── backend/
│   ├── main.py                    # FastAPI app entry
│   ├── database/
│   │   ├── db.py                  # Database connection
│   │   └── models.py              # SQLAlchemy models
│   ├── routers/
│   │   ├── auth.py                # Login endpoints
│   │   ├── students.py            # Student endpoints
│   │   └── admin.py               # Admin endpoints
│   ├── auth/
│   │   ├── hashing.py             # Password hashing
│   │   ├── jwt.py                 # Token creation
│   │   └── dependencies.py        # RBAC guards
│   ├── utils/
│   │   └── seed_data.py           # Database seeding ← FIXED
│   └── campus.db                  # SQLite database
│
├── frontend/
│   ├── public/
│   │   ├── login.html             # Login page ← UPDATED
│   │   ├── student/
│   │   │   └── dashboard.html     # Student dashboard
│   │   └── admin/
│   │       └── dashboard.html     # Admin dashboard
│   ├── scripts/
│   │   └── auth.js                # Auth utilities
│   └── styles/
│       └── main.css               # Shared styles
│
├── docs/
│   ├── STUDENT_LOGIN_TESTING.md   # Testing guide ← NEW
│   └── ...
│
├── README.md                       # Main documentation ← UPDATED
├── QUICKSTART_STUDENT_LOGIN.md     # Quick reference ← NEW
└── setup_and_run.sh                # Setup script ← NEW
```

## Summary of Changes

### Files Modified
1. ✅ `backend/utils/seed_data.py` - Added Student record for student@campus.edu
2. ✅ `backend/utils/seed_data.py` - Added User accounts for Alice & Bob
3. ✅ `README.md` - Updated test credentials
4. ✅ `frontend/public/login.html` - Updated demo credentials

### Files Created
1. ✅ `docs/STUDENT_LOGIN_TESTING.md` - Comprehensive testing guide
2. ✅ `QUICKSTART_STUDENT_LOGIN.md` - Quick reference
3. ✅ `setup_and_run.sh` - Automated setup script
4. ✅ `docs/STUDENT_LOGIN_ARCHITECTURE.md` - This file

### What Now Works
- ✅ Student login with `student@campus.edu`
- ✅ Student dashboard loads correctly
- ✅ Profile data displays properly
- ✅ All 5 student accounts functional
- ✅ RBAC properly enforced
- ✅ JWT authentication working

## Next Steps for Development

1. **Module 3**: Implement update request workflow
2. **File Upload**: Allow students to upload documents
3. **Email Notifications**: Notify students of changes
4. **Password Reset**: Implement forgot password flow
5. **Profile Pictures**: Add photo upload and display
6. **Audit Trail**: Enhanced logging for student actions

---

**Status**: ✅ Student login is fully functional and properly documented!
