# Module 1 – Authentication & RBAC

This document defines the **complete authentication layer** for the Campus Data Workflow Automation System.

It includes:

* Database schema
* JWT-based authentication
* Role-based access control
* Backend routes
* Minimal frontend (HTML + JS)

This module builds directly on **Module 0 – Foundation**.

---

## 🎯 Module Objective

Provide secure authentication and role-based access using **JWT tokens**, without over-engineering.

---

## 🗂️ Folder Structure (Module 1)

```
backend/
│
├── database/
│   └── models.py          # User table
│
├── auth/
│   ├── hashing.py         # Password hashing
│   ├── jwt.py             # JWT utilities
│   └── dependencies.py   # RBAC guards
│
├── routers/
│   └── auth.py            # Auth routes
│
├── main.py
│
frontend/
├── public/
│   ├── login.html
│   └── dashboard.html
```

---

## 🧱 1. Database Schema (User Model)

```python
# backend/database/models.py

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🔐 2. Password Hashing Utility

```python
# backend/auth/hashing.py

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

---

## 🔑 3. JWT Utilities

```python
# backend/auth/jwt.py

from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "CHANGE_ME_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

## 🛂 4. RBAC Dependencies

```python
# backend/auth/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from auth.jwt import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def require_role(required_role: str):
    def role_checker(user=Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return role_checker
```

---

## 🔌 5. Authentication Routes

```python
# backend/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User
from auth.hashing import verify_password
from auth.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user.email,
        "role": user.role
    })

    return {"access_token": token, "token_type": "bearer"}
```

---

## 🧠 6. Register Router in Main App

```python
# backend/main.py

from fastapi import FastAPI
from routers import auth

app = FastAPI()
app.include_router(auth.router)
```

---

## 🌐 7. Frontend – Login Page

```html
<!-- frontend/public/login.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Login</title>
</head>
<body>
  <h2>Login</h2>
  <form id="loginForm">
    <input type="email" id="email" placeholder="Email" required />
    <input type="password" id="password" placeholder="Password" required />
    <button type="submit">Login</button>
  </form>

  <script>
    document.getElementById("loginForm").addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData();
      formData.append("username", email.value);
      formData.append("password", password.value);

      const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      window.location.href = "dashboard.html";
    });
  </script>
</body>
</html>
```

---

## 🖥️ 8. Frontend – Dashboard

```html
<!-- frontend/public/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Dashboard</title>
</head>
<body>
  <h2>Dashboard</h2>
  <p>You are logged in.</p>

  <script>
    const token = localStorage.getItem("token");
    if (!token) window.location.href = "login.html";
  </script>
</body>
</html>
```

---

## ✅ Module Completion Criteria

* User can log in
* JWT token is issued
* Token stored in browser
* Protected routes ready
* Role-based checks supported

---

## 🔜 Next Module

Module 2 – Student Read Module
