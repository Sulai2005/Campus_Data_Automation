"""Authentication routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User
from auth.hashing import verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    
    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session
    
    Returns:
        Access token and token type
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email (username field contains email)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
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
        "role": user.role  # Include role for frontend routing
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
