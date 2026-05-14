"""
Logging configuration using Python's stdlib logging.

Call `setup_logging()` once during app startup to configure
structured, consistent log output across uvicorn, sqlalchemy, and app code.
"""

import logging
import sys

from core.config import get_settings

def setup_logging() -> None:
    """Configure stdlib logging with a consistent format for the entire app."""
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Shared formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)

    # Root logger
    logging.root.handlers = [console]
    logging.root.setLevel(level)

    # Quieten noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)

    logging.getLogger(__name__).info("Logging configured — level=%s", settings.log_level.upper())
