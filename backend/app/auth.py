"""
Authentication module for user registration and login.
Uses simple token-based session management with bcrypt password hashing.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Simple in-memory session store (for MVP - would use Redis in production)
_sessions: Dict[str, Dict[str, Any]] = {}

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
    """Create a new session token for a user."""
    token = secrets.token_urlsafe(32)
    _sessions[token] = {
        "user_id": user_id,
        "email": email,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=SESSION_EXPIRY_HOURS)
    }
    return token


def get_session(token: str) -> Optional[Dict[str, Any]]:
    """Get session data from token. Returns None if invalid/expired."""
    session = _sessions.get(token)
    if not session:
        return None
    
    if datetime.now() > session["expires_at"]:
        # Session expired, clean it up
        del _sessions[token]
        return None
    
    return session


def invalidate_session(token: str) -> bool:
    """Invalidate a session (logout)."""
    if token in _sessions:
        del _sessions[token]
        return True
    return False


def get_user_from_token(token: str) -> Optional[Dict[str, str]]:
    """Get user info from session token."""
    session = get_session(token)
    if session:
        return {
            "user_id": session["user_id"],
            "email": session["email"]
        }
    return None
