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
#
# ⚠️  BCRYPT 72-BYTE LIMIT FIX:
# bcrypt silently truncates OR raises ValueError
# for passwords longer than 72 bytes.
# Solution: pre-hash with SHA-256 (32 bytes output)
# BEFORE passing to bcrypt → no truncation ever.
#
# Flow:  plain_password
#           → SHA-256 (hex digest = 64 chars, always < 72 bytes)
#           → bcrypt hash  (stored in DB)
#
# This is a well-known pattern called "pepper + prehash"
# and is safe as long as you do the same on verify.

import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash(plain: str) -> str:
    """
    SHA-256 pre-hash to avoid bcrypt's 72-byte limit.
    Always produces a 64-char hex string — well within limit.
    """
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def hash_password(plain: str) -> str:
    """
    Hash a plain-text password safely:
      1. SHA-256 → 64-char hex  (bypasses bcrypt 72-byte limit)
      2. bcrypt  → stored hash
    """
    return pwd_context.hash(_prehash(plain))


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify plain password against stored bcrypt hash.
    Must prehash the same way as hash_password().
    """
    return pwd_context.verify(_prehash(plain), hashed)


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