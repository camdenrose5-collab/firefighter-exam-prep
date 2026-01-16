"""
Rate Limiting Configuration for Firefighter Exam Prep API

Uses slowapi to limit requests to AI-powered endpoints.
Prevents abuse and controls costs.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Use client IP for rate limiting
# In production behind Cloud Run, X-Forwarded-For is used automatically
limiter = Limiter(key_func=get_remote_address)


# Rate limit configurations
class RateLimits:
    """
    Rate limit strings for different endpoint types.
    Format: "count/period" where period is second, minute, hour, day
    """
    AI_GENERATE = "10/minute"      # Single AI generation calls
    AI_BATCH = "5/minute"          # Batch generation (heavier operations)
    STANDARD = "60/minute"         # Standard API calls
    AUTH = "20/minute"             # Auth endpoints (prevent brute force)


def get_rate_limit_exceeded_handler():
    """Return the rate limit exceeded error handler."""
    return _rate_limit_exceeded_handler
