from litestar.middleware import DefineMiddleware
from litestar.middleware.rate_limit import RateLimitMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send
import os
from datetime import timedelta

# Rate limiting middleware
rate_limit_middleware = DefineMiddleware(
    RateLimitMiddleware,
    rate_limit=("100/minute", "1000/hour"),
    exclude=["/health", "/docs"]
)

# Trusted hosts middleware
trusted_host_middleware = DefineMiddleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com"]
)

# Security headers middleware
async def security_headers_middleware(
    scope: Scope, receive: Receive, send: Send, app: ASGIApp
) -> None:
    """Adds various security headers to the response."""
    response = await app(scope, receive, send)
    response.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    })
    return response