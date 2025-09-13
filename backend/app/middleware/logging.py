"""
Centralized logging configuration for the Litestar application.

This module configures `structlog` to produce structured, machine-readable
logs in a JSON format, with a fallback to human-readable console output.
"""
import sys
import logging
import structlog
from structlog.typing import Processor, Filtering
from app.config import settings

def get_processors() -> list[Processor | Filtering]:
    """Get a list of structlog processors based on environment."""
    processors: list[Processor | Filtering] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_logger_name,
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

    if settings.debug:
        # Use a human-readable formatter for development
        processors.append(structlog.processors.ExceptionPrettyPrinter())
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Use a JSON formatter for production
        processors.append(structlog.processors.JSONRenderer())

    return processors

def setup_logging() -> None:
    """Set up the structlog configuration."""
    structlog.configure(
        processors=get_processors(),
        wrapper_class=structlog.make_filtering_bound_logger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    # Configure the standard logging library to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []

# This call will run the setup when the module is imported.
setup_logging()