from slowapi import Limiter
from slowapi.util import get_remote_address

# slowapi 0.1.x calls key_func synchronously (no await), so it can't read
# the request body (email) without a body-caching middleware -- rate
# limiting is per-IP here; per-account brute-force protection is the
# lockout in app/services/auth_service.py, keyed by email instead.
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
