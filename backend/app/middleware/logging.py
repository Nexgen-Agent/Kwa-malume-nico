import time
import logging
from litestar import Request, Response
from litestar.middleware import AbstractMiddleware

logger = logging.getLogger("api")

class LoggingMiddleware(AbstractMiddleware):
    async def _call_(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url} - {type(e)._name_}: {str(e)} - {duration:.3f}s"
            )
            raise

        duration = time.time() - start_time
        logger.info(
            f"{request.method} {request.url} - {response.status_code} - {duration:.3f}s"
        )
        
        return response
