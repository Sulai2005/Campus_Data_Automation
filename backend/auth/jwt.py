"""JWT token generation and configuration"""

from datetime import datetime, timedelta
from jose import jwt

# Configuration
SECRET_KEY = "CHANGE_ME_IN_PRODUCTION_USE_ENV_VARIABLE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing user information (sub, role, etc.)
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
