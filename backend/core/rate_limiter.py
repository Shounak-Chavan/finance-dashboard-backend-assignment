from slowapi import Limiter
from slowapi.util import get_remote_address
from backend.core.config import settings

# Global limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_MAX_REQUESTS}/minute"]  # global default
)