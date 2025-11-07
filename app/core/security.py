from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import jwt_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==============================
# Password utils
# ==============================
def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    
    Args:
        password (str): Plain text password.
    
    Returns:
        str: Hashed password.
    """
    safe_password = password[:72]
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password (str): Plain text password.
        hashed_password (str): Hashed password.
    
    Returns:
        bool: True if match, False otherwise.
    """
    safe_password = plain_password[:72]
    return pwd_context.verify(safe_password, hashed_password)


# ==============================
# JWT utils
# ==============================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data (dict): Payload data (e.g., {"sub": email}).
        expires_delta (timedelta, optional): Expiration time. Defaults to jwt_settings.access_token_expire_minutes.
    
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=jwt_settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, jwt_settings.secret_key, algorithm=jwt_settings.algorithm)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT refresh token (usually longer-lived than access token).
    
    Args:
        data (dict): Payload data (e.g., {"sub": email}).
        expires_delta (timedelta, optional): Expiration time. Defaults to 7 days.
    
    Returns:
        str: Encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, jwt_settings.secret_key, algorithm=jwt_settings.algorithm)


def verify_token(token: str) -> dict | None:
    """
    Verify a JWT token and return its payload.
    
    Args:
        token (str): JWT token to verify.
    
    Returns:
        dict | None: Decoded payload if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, jwt_settings.secret_key, algorithms=[jwt_settings.algorithm])
        return payload
    except JWTError:
        return None
