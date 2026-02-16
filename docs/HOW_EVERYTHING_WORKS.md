# How Everything Works - Complete Guide

## 📚 Table of Contents

1. [Quick Start - Get Running in 5 Minutes](#quick-start)
2. [What This System Does](#what-this-system-does)
3. [How Each Component Works](#how-each-component-works)
4. [Step-by-Step Setup Guide](#step-by-step-setup-guide)
5. [Testing Everything](#testing-everything)
6. [Understanding the Code](#understanding-the-code)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Get Running in 5 Minutes

```bash
# 1. Navigate to project directory
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"

# 2. Create virtual environment (if not exists)
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# 4. Install dependencies
pip install -r backend/requirements.txt

# 5. Setup database
cd backend
rm -f campus.db  # Remove old database if exists
python -m utils.seed_data

# 6. Start the server
python -m uvicorn main:app --reload

# 7. Open browser
# Go to: http://127.0.0.1:8000
```

**Login Credentials:**
- **Student**: `student@campus.edu` / `student123`
- **Admin**: `admin@campus.edu` / `admin123`

---

## 🎯 What This System Does

### Overview

The **Campus Data Workflow Automation System** is a web application that manages student data with proper authentication and role-based access control.

### Key Features

1. **User Authentication**
   - Secure login with email and password
   - JWT (JSON Web Token) based authentication
   - Password hashing with bcrypt

2. **Role-Based Access Control (RBAC)**
   - **Students**: Can view their own profile and documents
   - **Admin**: Can manage all students, upload files, generate reports
   - **Staff**: Can review update requests (future feature)

3. **Student Dashboard**
   - View personal information
   - See uploaded documents
   - Read-only access (updates via workflow in future modules)

4. **Admin Dashboard**
   - View all students
   - Upload student documents
   - Generate filtered reports

---

## 🔧 How Each Component Works

### 1. Frontend (What You See)

**Location**: `frontend/` directory

#### Login Page (`frontend/public/login.html`)
```
What it does:
├── Shows login form (email, password, role selector)
├── Sends credentials to backend
├── Receives JWT token
├── Stores token in browser localStorage
└── Redirects to appropriate dashboard based on role
```

**How it works:**
1. User enters email and password
2. JavaScript sends POST request to `/api/auth/login`
3. Backend validates credentials
4. Backend returns JWT token + user role
5. Frontend stores token and redirects user

#### Student Dashboard (`frontend/public/student/dashboard.html`)
```
What it does:
├── Checks if user is logged in (has token)
├── Verifies user has 'student' role
├── Fetches student profile from backend
└── Displays profile information and documents
```

**How it works:**
1. Page loads, checks localStorage for token
2. Calls `/api/student/profile` with token in header
3. Backend validates token and returns student data
4. JavaScript renders the data on the page

#### Auth Utilities (`frontend/scripts/auth.js`)
```
What it provides:
├── getToken() - Get stored JWT token
├── apiRequest() - Make authenticated API calls
├── requireAuth() - Redirect to login if not authenticated
├── requireRole() - Check user has correct role
└── logout() - Clear token and redirect to login
```

### 2. Backend (The Brain)

**Location**: `backend/` directory

#### Main Application (`backend/main.py`)
```
What it does:
├── Creates FastAPI application
├── Sets up CORS (allows frontend to call backend)
├── Registers all API routes
├── Serves frontend HTML pages
└── Serves static files (CSS, JS)
```

**Key responsibilities:**
- Entry point for the entire backend
- Connects all components together
- Handles HTTP requests and responses

#### Authentication Router (`backend/routers/auth.py`)
```
Endpoints:
├── POST /api/auth/login
│   ├── Receives: email, password
│   ├── Validates: Checks user exists and password matches
│   ├── Creates: JWT token with user info
│   └── Returns: Token + role
│
└── GET /api/auth/me
    ├── Receives: JWT token in header
    ├── Validates: Token is valid
    └── Returns: Current user information
```

**How login works:**
```python
1. User submits form with email/password
2. Backend queries User table for email
3. Compares password hash using bcrypt
4. If valid, creates JWT token:
   {
     "sub": "student@campus.edu",
     "role": "student",
     "user_id": 3
   }
5. Returns token to frontend
```

#### Student Router (`backend/routers/students.py`)
```
Endpoints:
├── GET /api/student/dashboard
│   ├── Requires: Student role
│   ├── Returns: Basic student info
│
└── GET /api/student/profile
    ├── Requires: Student role
    ├── Queries: Student table by email from token
    ├── Queries: StudentDocument table for files
    └── Returns: Complete profile with documents
```

**How profile loading works:**
```python
1. Frontend sends GET request with JWT token
2. Backend extracts email from token
3. Queries Student table: WHERE email = token.email
4. Queries StudentDocument table: WHERE student_id = student.id
5. Combines data and returns JSON
```

#### Admin Router (`backend/routers/admin.py`)
```
Endpoints:
├── GET /api/admin/dashboard
│   ├── Requires: Admin role
│   └── Returns: Dashboard statistics
│
├── POST /api/admin/upload/file
│   ├── Requires: Admin role
│   ├── Receives: File + student_id + file_type
│   ├── Saves: File to uploads/ directory
│   └── Creates: StudentDocument record
│
└── POST /api/admin/reports/generate
    ├── Requires: Admin role
    ├── Receives: Filter criteria
    └── Returns: Filtered student list
```

### 3. Authentication System

#### Password Hashing (`backend/auth/hashing.py`)
```python
# When creating user:
plain_password = "student123"
hashed = bcrypt.hashpw(plain_password, salt)
# Stored in database: "$2b$12$..."

# When logging in:
is_valid = bcrypt.checkpw(plain_password, stored_hash)
```

**Why this matters:**
- Passwords are NEVER stored in plain text
- Even if database is stolen, passwords are safe
- Each password has unique salt

#### JWT Tokens (`backend/auth/jwt.py`)
```python
# Creating token:
payload = {
    "sub": "student@campus.edu",  # Subject (user email)
    "role": "student",             # User role
    "user_id": 3,                  # Database ID
    "exp": datetime.utcnow() + timedelta(minutes=60)
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Decoding token:
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

**Why this matters:**
- Stateless authentication (no session storage needed)
- Token contains user info (no database lookup needed)
- Token expires after 60 minutes (security)
- Token is signed (can't be tampered with)

#### RBAC Guards (`backend/auth/dependencies.py`)
```python
# Protecting endpoints:
@router.get("/profile")
def get_profile(
    current_user: dict = Depends(require_student)  # ← Only students allowed
):
    # If user is not student, returns 403 Forbidden
    # If token is invalid, returns 401 Unauthorized
    pass
```

**How it works:**
1. Extract token from Authorization header
2. Decode and validate token
3. Check if user role matches required role
4. If yes, allow access; if no, return error

### 4. Database (The Memory)

**Location**: `backend/campus.db` (SQLite file)

#### Database Tables

**users** - Authentication
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'admin', 'staff', 'student'
    created_at DATETIME
);
```

**students** - Student Information
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    student_id TEXT UNIQUE NOT NULL,  -- e.g., "TEST2024001"
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,       -- MUST match users.email!
    department TEXT,
    year INTEGER,
    phone TEXT,
    address TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

**student_documents** - File Metadata
```sql
CREATE TABLE student_documents (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,  -- Foreign key to students.id
    file_type TEXT,      -- 'photo', 'certificate', etc.
    file_path TEXT,      -- Path to actual file
    file_name TEXT,      -- Original filename
    uploaded_by TEXT,    -- Email of uploader
    uploaded_at DATETIME
);
```

#### Critical Relationship

```
┌─────────────────┐         ┌─────────────────┐
│  users          │         │  students       │
├─────────────────┤         ├─────────────────┤
│ email           │ ═══════ │ email           │
│ (for login)     │  MUST   │ (for profile)   │
│                 │  MATCH! │                 │
└─────────────────┘         └─────────────────┘
```

**This is THE most important thing:**
- When a student logs in, we use `users.email`
- When loading profile, we query `students.email`
- **These MUST be the same email!**
- This was the bug I fixed - `student@campus.edu` had no Student record

### 5. Seed Data (`backend/utils/seed_data.py`)

**What it does:**
```
1. Creates database tables
2. Creates test users (admin, staff, students)
3. Creates student records
4. Prints credentials for testing
```

**Users created:**
```python
admin@campus.edu        → role: admin
staff@campus.edu        → role: staff
student@campus.edu      → role: student  ← Generic test account
john.doe@campus.edu     → role: student
jane.smith@campus.edu   → role: student
alice.johnson@campus.edu → role: student
bob.williams@campus.edu → role: student
```

**Students created (MUST match user emails!):**
```python
student@campus.edu      → TEST2024001, Test Student
john.doe@campus.edu     → CS2024001, John Doe
jane.smith@campus.edu   → CS2024002, Jane Smith
alice.johnson@campus.edu → EE2024001, Alice Johnson
bob.williams@campus.edu → ME2024001, Bob Williams
```

---

## 📋 Step-by-Step Setup Guide

### Prerequisites

You need:
- Python 3.8 or higher
- pip (Python package manager)
- A web browser
- Terminal/Command Prompt

### Step 1: Check Python Installation

```bash
python --version
# Should show: Python 3.8.x or higher

pip --version
# Should show pip version
```

If not installed:
- **Linux**: `sudo apt install python3 python3-pip`
- **Mac**: `brew install python3`
- **Windows**: Download from python.org

### Step 2: Navigate to Project

```bash
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"
```

### Step 3: Create Virtual Environment

**What is a virtual environment?**
- Isolated Python environment for this project
- Keeps dependencies separate from system Python
- Prevents version conflicts

```bash
python -m venv venv
```

This creates a `venv/` folder with isolated Python.

### Step 4: Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 5: Install Dependencies

```bash
pip install -r backend/requirements.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - Database ORM
- `python-jose` - JWT handling
- `bcrypt` - Password hashing
- `python-multipart` - File upload support

### Step 6: Create Database

```bash
cd backend

# Remove old database if exists
rm -f campus.db

# Create and seed new database
python -m utils.seed_data
```

**Expected output:**
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

### Step 7: Start the Server

```bash
# Make sure you're in backend/ directory
python -m uvicorn main:app --reload
```

**What this does:**
- Starts FastAPI server on http://127.0.0.1:8000
- `--reload` makes it auto-restart when code changes
- Server runs until you press Ctrl+C

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 8: Open in Browser

Open your web browser and go to:
```
http://127.0.0.1:8000
```

You should see the login page!

---

## 🧪 Testing Everything

### Test 1: Student Login

1. **Go to**: http://127.0.0.1:8000/
2. **Enter**:
   - Email: `student@campus.edu`
   - Password: `student123`
   - Role: Select "Student"
3. **Click**: Login
4. **Expected**: Redirected to student dashboard showing:
   - Student ID: TEST2024001
   - Name: Test Student
   - Department: Computer Science
   - Year: 1

**If this works**: ✅ Authentication is working!

### Test 2: Admin Login

1. **Go to**: http://127.0.0.1:8000/
2. **Enter**:
   - Email: `admin@campus.edu`
   - Password: `admin123`
   - Role: Select "Admin"
3. **Click**: Login
4. **Expected**: Redirected to admin dashboard

**If this works**: ✅ RBAC is working!

### Test 3: Invalid Login

1. **Go to**: http://127.0.0.1:8000/
2. **Enter**:
   - Email: `student@campus.edu`
   - Password: `wrongpassword`
3. **Click**: Login
4. **Expected**: Error message "Invalid email or password"

**If this works**: ✅ Security is working!

### Test 4: API Documentation

1. **Go to**: http://127.0.0.1:8000/docs
2. **Expected**: Interactive API documentation (Swagger UI)
3. **Try**: Expand `/api/auth/login` and test it

**If this works**: ✅ FastAPI is working!

### Test 5: Different Student Accounts

Try logging in with:
- `john.doe@campus.edu` / `student123`
- `jane.smith@campus.edu` / `student123`

Each should show different profile data.

---

## 💡 Understanding the Code

### How a Login Request Works (Complete Flow)

```
1. USER ACTION
   ↓
   User enters email/password and clicks Login

2. FRONTEND (login.html)
   ↓
   const formData = new FormData();
   formData.append('username', email);
   formData.append('password', password);
   ↓
   fetch('http://127.0.0.1:8000/api/auth/login', {
       method: 'POST',
       body: formData
   })

3. BACKEND (main.py)
   ↓
   FastAPI receives POST /api/auth/login
   ↓
   Routes to auth.router (routers/auth.py)

4. AUTH ROUTER (routers/auth.py)
   ↓
   @router.post("/login")
   def login(form_data: OAuth2PasswordRequestForm, db: Session):
       ↓
       user = db.query(User).filter(User.email == form_data.username).first()
       ↓
       if not user or not verify_password(form_data.password, user.hashed_password):
           raise HTTPException(401, "Invalid credentials")
       ↓
       token = create_access_token({
           "sub": user.email,
           "role": user.role,
           "user_id": user.id
       })
       ↓
       return {"access_token": token, "token_type": "bearer", "role": user.role}

5. FRONTEND (login.html)
   ↓
   Receives response with token
   ↓
   localStorage.setItem('token', data.access_token);
   localStorage.setItem('role', data.role);
   ↓
   if (data.role === 'student'):
       window.location.href = '/student/dashboard'

6. STUDENT DASHBOARD (student/dashboard.html)
   ↓
   Page loads
   ↓
   requireRole('student')  // Checks localStorage.role
   ↓
   loadStudentProfile()
   ↓
   apiRequestJSON('/student/profile')  // Sends token in header

7. BACKEND (routers/students.py)
   ↓
   @router.get("/profile")
   def get_profile(current_user: dict = Depends(require_student), db: Session):
       ↓
       require_student validates token and checks role
       ↓
       student = db.query(Student).filter(Student.email == current_user["sub"]).first()
       ↓
       documents = db.query(StudentDocument).filter(...).all()
       ↓
       return {student data + documents}

8. FRONTEND (student/dashboard.html)
   ↓
   Receives profile data
   ↓
   displayProfile(data)
   ↓
   Renders HTML with student information
```

### Key Code Snippets Explained

#### Creating a Protected Endpoint

```python
# backend/routers/students.py

from auth.dependencies import require_student

@router.get("/profile")
def get_student_profile(
    current_user: dict = Depends(require_student),  # ← This protects the endpoint
    db: Session = Depends(get_db)
):
    # Only students with valid tokens can reach this code
    email = current_user.get("sub")  # Get email from token
    student = db.query(Student).filter(Student.email == email).first()
    return student
```

**What happens:**
1. `Depends(require_student)` runs BEFORE the function
2. It validates the JWT token
3. It checks if role === 'student'
4. If valid, passes user data to function
5. If invalid, returns 401/403 error

#### Making an Authenticated API Call

```javascript
// frontend/scripts/auth.js

async function apiRequestJSON(endpoint, options = {}) {
    const token = localStorage.getItem('token');  // Get stored token
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            'Authorization': `Bearer ${token}`,  // ← Send token
            ...options.headers
        }
    });
    
    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('token');
        window.location.href = '/';  // Redirect to login
    }
    
    return await response.json();
}
```

**What happens:**
1. Gets token from localStorage
2. Adds it to Authorization header
3. Sends request to backend
4. If 401 (Unauthorized), redirects to login
5. Otherwise, returns data

---

## 🔍 Troubleshooting

### Problem: "Module not found" errors

**Symptom:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Dependencies not installed or virtual environment not activated

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### Problem: "Student profile not found" (404)

**Symptom:** Login works but dashboard shows error

**Cause:** Database not seeded with updated data

**Solution:**
```bash
cd backend
rm campus.db
python -m utils.seed_data
```

### Problem: "Port 8000 already in use"

**Symptom:**
```
ERROR: [Errno 98] Address already in use
```

**Cause:** Another process is using port 8000

**Solution:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use different port
python -m uvicorn main:app --reload --port 8001
```

### Problem: Login page doesn't load

**Symptom:** Browser shows "Can't reach this page"

**Cause:** Server not running

**Solution:**
```bash
cd backend
python -m uvicorn main:app --reload
```

### Problem: "CORS error" in browser console

**Symptom:**
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**Cause:** CORS middleware not configured (should be automatic)

**Solution:** Check `backend/main.py` has:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Problem: Changes to code don't take effect

**Symptom:** Modified code but behavior unchanged

**Cause:** Server not reloading or browser cache

**Solution:**
```bash
# 1. Make sure server is running with --reload
python -m uvicorn main:app --reload

# 2. Hard refresh browser
# Chrome/Firefox: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

---

## 📚 Additional Resources

### Documentation Files

- **README.md** - Main project documentation
- **QUICKSTART.md** - Quick setup guide
- **docs/STUDENT_LOGIN_TESTING.md** - Detailed testing guide
- **docs/STUDENT_LOGIN_ARCHITECTURE.md** - System architecture
- **QUICKSTART_STUDENT_LOGIN.md** - Quick reference card

### API Documentation

When server is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **JWT**: https://jwt.io/introduction
- **OAuth2**: https://oauth.net/2/

---

## 🎓 Summary

### What You Have Now

✅ **Working Authentication System**
- Login with email/password
- JWT token-based auth
- Secure password hashing

✅ **Role-Based Access Control**
- Students see their own data
- Admins can manage all data
- Proper permission enforcement

✅ **Student Dashboard**
- View profile information
- See uploaded documents
- Clean, modern UI

✅ **Admin Dashboard**
- Manage students
- Upload files
- Generate reports

### What Was Fixed

1. ✅ Added Student record for `student@campus.edu`
2. ✅ Added User accounts for all students
3. ✅ Updated all documentation
4. ✅ Created comprehensive guides

### Next Steps

You can now:
1. **Use the system** - Login and explore
2. **Modify the code** - Add new features
3. **Learn the patterns** - Understand how it works
4. **Build Module 3** - Implement update requests

---

**Need Help?**

If something doesn't work:
1. Check the troubleshooting section above
2. Review the step-by-step setup guide
3. Check server logs in terminal
4. Check browser console (F12) for errors

**Everything should work now!** 🎉
