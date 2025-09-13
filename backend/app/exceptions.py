from litestar import Request, Response
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
import logging

logger = logging.getLogger("api")

async def global_exception_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, HTTPException):
        return Response(
            content={"detail": exc.detail},
            status_code=exc.status_code,
        )

    # Log unexpected errors
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return Response(
        content={"detail": "Internal server error"},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )