"""
Structured logging setup using loguru.
"""

import sys
from pathlib import Path

from loguru import logger

from config.settings import Config


def setup_logging(log_level: str = None) -> "logger":
    """
    Configure loguru logger with file and console handlers.

    Returns:
        Configured logger instance.
    """
    log_level = log_level or Config.LOG_LEVEL
    logs_dir = Config.LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Console handler (only if stdout is available; may be None in PyInstaller --windowed)
    if sys.stdout is not None:
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
        )

    # File handler
    log_file = logs_dir / "bot_{time:YYYYMMDD}.log"
    logger.add(
        str(log_file),
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention=f"{Config.LOG_RETENTION_DAYS} days",
        enqueue=True,
    )

    return logger


# Module-level logger
log = setup_logging()
