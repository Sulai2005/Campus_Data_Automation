"""Authentication routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from database.db import get_db
from database.models import User
from auth.hashing import verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    role: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token with role validation
    
    Args:
        username: User email
        password: User password
        role: Selected role from frontend (optional but recommended)
        db: Database session
    
    Returns:
        Access token, token type, and user role
    
    Raises:
        HTTPException: If credentials are invalid or role mismatch
    """
    # Find user by email
    user = db.query(User).filter(User.email == username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate role if provided
    if role and role.lower() != user.role.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. This account is registered as '{user.role}', but you selected '{role}'. Please select the correct role.",
        )
    
    # Create JWT token with user info
    token = create_access_token({
        "sub": user.email,
        "role": user.role,
        "user_id": user.id
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role  # Return actual role for frontend routing
    }


@router.get("/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Args:
        current_user: User payload from JWT token
    
    Returns:
        User information
    """
    return {
        "email": current_user.get("sub"),
        "role": current_user.get("role"),
        "user_id": current_user.get("user_id")
    }
