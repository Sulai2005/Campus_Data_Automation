# Campus Data Workflow Automation System

---

## Technical Architecture & Project Structure

### Project Overview

The **Campus Data Workflow Automation System (CDWAS)** is a centralized backend system designed to manage institutional data using **controlled workflows**, **role-based access**, and **full auditability**.

The system is built with **FastAPI** and communicates with a simple frontend built using **HTML, CSS, and JavaScript**.

---

### Technology Stack

**Backend**

* Python 3.x
* FastAPI
* SQLAlchemy ORM
* SQLite (MVP / Development) or Postgres SQL (future migrations)
* Alembic (future migrations)

**Frontend**

* HTML
* CSS
* Vanilla JavaScript (Fetch API)

**Data Processing**

* Pandas (CSV / Excel ingestion)

---

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
│   ├── staff.py             # Staff workflows
│   ├── admin.py             # Admin controls
│
├── auth/                    # Authentication & RBAC logic
│   ├── hashing.py           # Password hashing
│   └── dependencies.py      # Role-based access guards
│
├── utils/                   # Shared utilities
│   ├── validators.py        # Field validation helpers
│   └── responses.py         # Common API responses
│
├── uploads/                 # Bulk upload handling
│   └── parser.py            # CSV / Excel parsing logic
│
├── audit/                   # Audit logging
│   └── logger.py            # Immutable audit trail
│
└── tests/                   # Testing & experiments
    └── main.py
```

---

### Architectural Principles

* **Router-Based Design**: All HTTP endpoints live inside the `routers/` folder
* **Separation of Concerns**: Auth, database, utilities, and routes are isolated
* **Workflow > CRUD**: Direct record edits are prohibited
* **Single Source of Truth**: PostgreSQL is the authoritative data store
* **Scalable by Design**: Easy to extend without breaking existing modules

---

### Role-Based Access Control (RBAC)

Supported roles:

* `student`
* `staff`
* `admin`

RBAC is enforced using FastAPI dependency injection via `auth/dependencies.py`.

---

### Frontend Integration

* Frontend communicates via REST APIs
* Uses JavaScript `fetch()` for async requests
* No frontend framework dependency

---

### Running the Application

```bash
uvicorn backend.main:app --reload
```

---
