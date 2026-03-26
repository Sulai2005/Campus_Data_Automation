"""Password hashing utilities using bcrypt directly"""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plain text password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        return hash_password(password)
    
    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)
