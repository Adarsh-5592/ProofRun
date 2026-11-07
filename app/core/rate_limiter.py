from slowapi import Limiter
from slowapi.util import get_remote_address


# In-memory rate limiter.
# For production with multiple workers, use shared storage such as Redis.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",
)
