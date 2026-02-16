# Quick Start Guide - Student Login

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 2: Seed Database
```bash
cd backend
python -m utils.seed_data
```

### Step 3: Start Server
```bash
python -m uvicorn main:app --reload
```

**Or use the automated script:**
```bash
./setup_and_run.sh
```

## 🔑 Test Credentials

### Student Accounts (Password: `student123`)
- `student@campus.edu` - Test Student
- `john.doe@campus.edu` - John Doe  
- `jane.smith@campus.edu` - Jane Smith
- `alice.johnson@campus.edu` - Alice Johnson
- `bob.williams@campus.edu` - Bob Williams

### Admin Account
- `admin@campus.edu` / `admin123`

### Staff Account
- `staff@campus.edu` / `staff123`

## 🌐 Access Points

- **Login Page**: http://127.0.0.1:8000/
- **Student Dashboard**: http://127.0.0.1:8000/student/dashboard
- **Admin Dashboard**: http://127.0.0.1:8000/admin/dashboard
- **API Docs**: http://127.0.0.1:8000/docs

## ✅ What Was Fixed

1. ✅ Added `Student` record for `student@campus.edu` (was missing)
2. ✅ Added `User` accounts for Alice Johnson and Bob Williams
3. ✅ Updated all documentation with correct credentials
4. ✅ Student login now works end-to-end

## 🧪 Quick Test

1. Navigate to http://127.0.0.1:8000/
2. Login with: `student@campus.edu` / `student123`
3. Should see student dashboard with profile data

## 📚 Full Documentation

See `docs/STUDENT_LOGIN_TESTING.md` for comprehensive testing guide.
