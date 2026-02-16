
## Development Plan & Module Roadmap

### Project Objective

Build a **workflow-driven institutional data system** that replaces spreadsheets and manual forms with governed digital processes.

---

### Development Philosophy

* MVP-first approach
* One module at a time
* Every stage must be runnable
* No premature optimization

---

### Module Breakdown

#### 🔹 Module 0 – Foundation

**Goal:** Establish backend base

**Includes:**

* Project structure
* Database connection
* Core models
* FastAPI app startup

**Output:** Backend runs and connects to DB

---

#### 🔹 Module 1 – Authentication & RBAC

**Goal:** Identify users and control access

**Includes:**

* Login system
* Password hashing
* Role-based route protection

**Output:** System knows who the user is and their permissions

---

#### 🔹 Module 2 – Student Read Module

**Goal:** Allow students to view their data

**Includes:**

* Student dashboard
* Read-only profile
* View update request history

---

#### 🔹 Module 3 – Update Request Workflow

**Goal:** Replace direct data editing

**Includes:**

* Submit update request
* Track request status
* Store old vs new values

**Status Flow:**

```
pending → approved → applied
pending → rejected → feedback
```

---

#### 🔹 Module 4 – Staff Review System

**Goal:** Controlled approvals

**Includes:**

* View pending requests
* Approve or reject
* Provide feedback

---

#### 🔹 Module 5 – Bulk Data Upload

**Goal:** Handle institutional data ingestion

**Includes:**

* CSV / Excel upload
* Validation preview
* Batch commit

---

#### 🔹 Module 6 – Audit Logging

**Goal:** Ensure accountability

**Includes:**

* Immutable audit logs
* Track sensitive actions
* Admin-only access

---

#### 🔹 Module 7 – Reporting

**Goal:** Generate institutional insights

**Includes:**

* Filtered reports
* CSV / PDF exports

---

### Final Outcome

By completing all modules, the project demonstrates:

* Backend architecture skills
* Workflow-based system design
* Secure data handling
* Real-world problem solving

---

### Documentation Note

This document acts as the **single source of truth** for system architecture and development order.
