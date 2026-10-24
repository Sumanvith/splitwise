from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=settings.redis_url,
    storage_options={
        "socket_connect_timeout": 5,
        "socket_timeout": 5,
        "health_check_interval": 30,
    },
    in_memory_fallback_enabled=True,  # Redis fails -> count in memory
    swallow_errors=False,             # no more view_rate_limit crash
)
