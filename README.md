# Campus Data Workflow Automation System

**Module-1 Prototype: Authentication & RBAC**

A professional, modular FastAPI backend with JWT authentication, role-based access control, and clean frontend separation.

---

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

**TL;DR:**
```bash
cd backend
pip install -r requirements.txt
python -m utils.seed_data
uvicorn main:app --reload
```

Then open your browser and navigate to: **http://127.0.0.1:8000**

**Test Credentials:**
- Admin: `admin@campus.edu` / `admin123`
- Student: `student@campus.edu` / `student123`
- Other Students: `john.doe@campus.edu`, `jane.smith@campus.edu`, etc. / `student123`

---

## 📋 Project Overview

The **Campus Data Workflow Automation System (CDWAS)** is a centralized backend system designed to manage institutional data using **controlled workflows**, **role-based access**, and **full auditability**.

### Key Features (Module-1)

✅ **JWT Authentication** - Secure token-based auth  
✅ **Role-Based Access Control** - Admin, Staff, Student roles  
✅ **Consolidated Database** - Single source of truth  
✅ **File Upload System** - Photos, documents with metadata  
✅ **Modular Reports System** - Customizable student reports with filters  
✅ **Separate Admin Pages** - Dashboard, Upload, Reports  
✅ **Student Dashboard** - Read-only profile view  
✅ **Sample Data Generator** - Create test student data  
✅ **Complete Test Suite** - Auth, RBAC, integration tests  

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.x
- FastAPI
- SQLAlchemy ORM
- SQLite (MVP) / PostgreSQL (production-ready)
- JWT (python-jose)
- Bcrypt (password hashing)

**Frontend:**
- HTML5
- CSS3 (Modern design system)
- Vanilla JavaScript (Fetch API)

**Testing:**
- Pytest
- httpx (FastAPI testing)

### Database Schema

```
users
├── id, email, hashed_password, role, created_at

students
├── id, student_id, name, email, department, year
├── phone, address, created_at, updated_at
└── relationships: documents, update_requests

student_documents
├── id, student_id (FK), file_type, file_path
├── file_name, uploaded_by, uploaded_at
└── relationship: student

audit_logs
├── id, user_id (FK), user_email, action
├── entity_type, entity_id, old_value, new_value
└── timestamp

update_requests
├── id, student_id (FK), field_name
├── old_value, new_value, status, reason, feedback
├── requested_at, reviewed_at, reviewed_by
└── relationship: student
```

### Backend Folder Structure

```
backend/
│
├── main.py                  # Application entry point
│
├── database/                # Database layer
│   ├── db.py                # DB connection & session
│   └── models.py            # SQLAlchemy models
│
├── routers/                 # All API routes
│   ├── auth.py              # Authentication routes
│   ├── students.py          # Student APIs
│   └── admin.py             # Admin controls
│
├── auth/                    # Authentication & RBAC logic
│   ├── hashing.py           # Password hashing
│   ├── jwt.py               # JWT token generation
│   └── dependencies.py      # Role-based access guards
│
├── services/                # Business logic layer
│   ├── upload_service.py    # File upload handling
│   └── report_service.py    # Report generation
│
├── utils/                   # Shared utilities
│   └── seed_data.py         # Database seeding
│
└── tests/                   # Testing suite
    ├── conftest.py          # Test configuration
    ├── test_auth.py         # Auth tests
    ├── test_rbac.py         # RBAC tests
    └── test_upload.py       # Upload tests
```

### Frontend Structure

```
frontend/
│
├── public/
│   ├── login.html           # Login page
│   ├── admin/
│   │   ├── dashboard.html   # Admin dashboard
│   │   ├── upload.html      # File upload page
│   │   └── reports.html     # Reports page
│   └── student/
│       └── dashboard.html   # Student dashboard
│
├── styles/
│   └── main.css             # Shared design system
│
└── scripts/
    └── auth.js              # Auth utilities & API helpers
```

---

## 🔐 Security Features

- **Password Hashing:** Bcrypt with salt
- **JWT Tokens:** HS256 algorithm, 60-minute expiry
- **RBAC Enforcement:** Dependency injection guards
- **Input Validation:** File type, size, and content checks
- **Audit Logging:** Immutable trail of sensitive actions
- **CORS Protection:** Configurable origins

---

## 🎯 Architectural Principles

1. **Router-Based Design:** All HTTP endpoints live inside `routers/`
2. **Separation of Concerns:** Auth, database, services, and routes are isolated
3. **Workflow > CRUD:** Direct record edits are prohibited
4. **Single Source of Truth:** Database is the authoritative data store
5. **Scalable by Design:** Easy to extend without breaking existing modules
6. **Test-Driven:** Every module includes comprehensive tests

---

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Admin (Protected)
- `GET /admin/dashboard` - Dashboard data
- `POST /admin/upload/file` - Upload student document
- `POST /admin/reports/generate` - Generate filtered report

### Student (Protected)
- `GET /student/dashboard` - Student dashboard data
- `GET /student/profile` - Detailed profile with documents

### Public
- `GET /` - API status
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

---

## 🧪 Testing

Run the complete test suite:

```bash
cd backend
pytest tests/ -v
```

**Test Coverage:**
- Authentication (login success/failure, token validation)
- RBAC (admin-only access, student-only access, denial)
- File Upload (success, validation, permissions)
- Integration tests

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Setup and installation guide
- **[PLAN.md](PLAN.md)** - Module roadmap and development plan
- **[MODULIZATION.md](MODULIZATION.md)** - Module-1 implementation details
- **[implementation_plan.md](brain/.../implementation_plan.md)** - Detailed design decisions

---

## 🗺️ Module Roadmap

- ✅ **Module 0:** Foundation (Database, FastAPI setup)
- ✅ **Module 1:** Authentication & RBAC (Current)
- 🔜 **Module 2:** Student Read Module (Enhanced)
- 🔜 **Module 3:** Update Request Workflow
- 🔜 **Module 4:** Staff Review System
- 🔜 **Module 5:** Bulk Data Upload
- 🔜 **Module 6:** Audit Logging (Enhanced)
- 🔜 **Module 7:** Advanced Reporting

---

## 🎨 Design Philosophy

**Professional & Modern:**
- Clean, intuitive UI
- Responsive design
- Consistent color scheme
- Accessible components

**Modular & Maintainable:**
- Clear separation of concerns
- Reusable components
- Well-documented code
- Comprehensive tests

**Secure & Auditable:**
- JWT-based authentication
- Role-based access control
- Audit trail for all actions
- Input validation

---

## 🚧 Future Enhancements

- PostgreSQL migration
- Email notifications
- Advanced reporting (PDF export)
- Bulk data upload (CSV/Excel)
- Document preview
- Update request workflow
- Staff approval system
- Enhanced audit logging

---

## 📝 License

This project is for educational and demonstration purposes.

---

## 🤝 Contributing

This is a learning project demonstrating:
- FastAPI best practices
- JWT authentication
- RBAC implementation
- Workflow-driven design
- Clean architecture

---

## 📞 Support

For issues or questions:
1. Check [QUICKSTART.md](QUICKSTART.md) for setup help
2. Review test files for usage examples
3. Check API docs at `/docs` endpoint

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern web standards.**
