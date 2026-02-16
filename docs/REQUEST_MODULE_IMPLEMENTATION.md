# Request Module Implementation - Feature Overview

## ✅ Features Implemented

### 1. **Student Request Portal** 🎓
**Location:** `/student/requests`
**Capabilities:**
- **Submit New Request:** Students can request changes for specific fields (Name, Department, Year, Phone, Address).
- **View History:** See a list of all past requests with their status (Pending, Approved, Rejected).
- **Status Tracking:** Visual badges for request status and feedback from admins.
- **Validation:** Prevents duplicate pending requests for the same field.

### 2. **Admin Review Portal** 🛡️
**Location:** `/admin/requests`
**Capabilities:**
- **Dashboard View:** See all requests in one place.
- **Filtering:** Filter requests by status (Pending, Approved, Rejected).
- **Detailed Review:** Modal view shows Old Value vs. New Value side-by-side.
- **Action:** Approve or Reject requests with optional feedback.
- **Auto-Update:** Approving a request automatically updates the student's profile in the database.

### 3. **Backend Logic** ⚙️
**Router:** `backend/routers/requests.py`
**Key Endpoints:**
- `POST /api/requests/`: Create request (Student only).
- `GET /api/requests/my`: Get my requests (Student only).
- `GET /api/requests/all`: Get all requests (Admin only).
- `PUT /api/requests/{id}/status`: Approve/Reject request (Admin only).

**Security & Validation:**
- **RBAC:** Strict role checking (Student vs. Admin).
- **Field Whitelist:** Only specific fields (`name`, `department`, `year`, `phone`, `address`) can be requested.
- **Ownership:** Students can only see their own requests.
- **Audit Logging:** All approvals are logged in `audit_logs` table.

## 🔄 Workflow

1.  **Student** navigates to "Requests" from Dashboard.
2.  **Student** clicks "New Request", selects "Phone Number", enters new number, and reason.
3.  **System** creates a `pending` request.
4.  **Admin** sees the request in their portal.
5.  **Admin** reviews the change (Old vs New).
6.  **Admin** clicks "Approve".
7.  **System**:
    - Updates the request status to `approved`.
    - **Updates the Student's Phone Number in the database.**
    - Logs the action in `AuditLog`.
8.  **Student** sees the status change to "Approved" on their dashboard.

## 📁 Files Created/Modified

**New Files:**
- `backend/routers/requests.py`
- `frontend/public/student/requests.html`
- `frontend/public/admin/requests.html`

**Modified Files:**
- `backend/main.py` (Registered router & pages)
- `frontend/public/student/dashboard.html` (Added links)
- `frontend/public/admin/dashboard.html` (Added links)

## 🚀 How to Test

1.  **Login as Student (`student@example.com` / `student123`)**
    - Go to Dashboard -> Requests.
    - Submit a request to change your "Phone Number".
    - You should see it in the list as "Pending".

2.  **Login as Admin (`admin@example.com` / `admin123`)**
    - Go to Dashboard -> Requests.
    - Find the pending request.
    - Click "Review".
    - Click "Approve".

3.  **Verify:**
    - Admin list shows "Approved".
    - **Student Profile** (Dashboard) now shows the NEW phone number.
