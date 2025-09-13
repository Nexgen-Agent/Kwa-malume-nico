import time
import logging
from litestar import Request, Response
from litestar.middleware import MiddlewareProtocol

logger = logging.getLogger("api")

class LoggingMiddleware(MiddlewareProtocol):
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive, send)
        start_time = time.time()

        try:
            await self.app(scope, receive, send)
            duration = time.time() - start_time
            response = Response(status_code=200)  # Dummy response, as the actual one is handled by the app
            logger.info(
                f"{request.method} {request.url} - {response.status_code} - {duration:.3f}s"
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url} - {type(e).__name__}: {str(e)} - {duration:.3f}s"
            )
            raise

