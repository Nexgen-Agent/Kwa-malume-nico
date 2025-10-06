"""
Centralized logging configuration for the Litestar application.
"""
from typing import List
import sys
import logging
import structlog
from structlog.typing import Processor
from app.config import settings


def get_processors() -> List[Processor]:
    """Get a list of structlog processors based on environment settings."""
    processors: List[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            }
        ),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.debug:  # ✅ correctly indented inside the function
        processors.append(structlog.processors.ExceptionPrettyPrinter())
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    return processors # ✅ safely inside function

def setup_logging() -> None:
    """Set up the structlog configuration."""
    structlog.configure(
        processors=get_processors(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []


setup_logging()