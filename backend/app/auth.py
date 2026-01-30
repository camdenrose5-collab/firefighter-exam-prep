"""
Authentication module for user registration and login.
Uses persistent database sessions (survives Cloud Run restarts).
Token-based session management with SHA-256 password hashing.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict

from . import db

SESSION_EXPIRY_HOURS = 24 * 7  # 1 week


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt (simple approach for MVP)."""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, hash_value = password_hash.split("$")
        check_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return check_hash == hash_value
    except Exception:
        return False


def create_session(user_id: str, email: str) -> str:
    """Create a new persistent session token for a user."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=SESSION_EXPIRY_HOURS)
    
    # Store in database (persists to Cloud Storage)
    db.create_session(token, user_id, email, expires_at)
    
    return token


def get_session(token: str) -> Optional[Dict[str, str]]:
    """Get session data from token. Returns None if invalid/expired."""
    return db.get_session(token)


def invalidate_session(token: str) -> bool:
    """Invalidate a session (logout)."""
    return db.delete_session(token)


def get_user_from_token(token: str) -> Optional[Dict[str, str]]:
    """Get user info from session token."""
    session = db.get_session(token)
    if session:
        return {
            "user_id": session["user_id"],
            "email": session["email"]
        }
    return None
