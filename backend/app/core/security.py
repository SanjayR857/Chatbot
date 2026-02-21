# ─────────────────────────────────────────────
# app/core/security.py
#
# PURPOSE: All cryptographic operations:
#   - Password hashing & verification (bcrypt)
#   - JWT access token creation & decoding
#
# WHY HERE? Security logic is used by multiple
# services. One place = one change if algo changes.
# ─────────────────────────────────────────────

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings

# ── Password hashing ──────────────────────────
# bcrypt automatically salts + hashes passwords.
# NEVER store plain-text passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    """Hash a plain-text password → bcrypt hash string"""
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """Compare plain password against stored hash"""
    return pwd_context.verify(plain, hashed)


# ── JWT Tokens ────────────────────────────────
# JWT = JSON Web Token
# Structure: header.payload.signature  (base64 encoded)
# Payload contains: user_id, expiry, token type
# Signature ensures nobody tampered with the payload

def create_access_token(user_id: int) -> str:
    """
    Creates a short-lived JWT (default: 60 min).
    Sent with every API request in Authorization header.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),   # subject = who this token belongs to
        "exp": expire,          # expiry timestamp
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """
    Creates a long-lived JWT (default: 7 days).
    Used to get a new access token without re-login.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodes & validates a JWT.
    Raises 401 if token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )