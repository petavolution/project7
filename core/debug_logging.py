#!/usr/bin/env python3
"""
Debug Logging System for MetaMindIQTrain

Provides comprehensive logging to both console and debug-log.txt file.
All critical errors and debug output are captured for troubleshooting.
"""

import logging
import sys
import os
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parent
DEBUG_LOG_FILE = PROJECT_ROOT / "debug-log.txt"


def setup_logging(level: int = logging.DEBUG,
                  console_level: int = logging.INFO,
                  log_file: Optional[Path] = None) -> logging.Logger:
    """
    Set up comprehensive logging to both console and file.

    Args:
        level: Minimum log level for file output
        console_level: Minimum log level for console output
        log_file: Path to log file (defaults to debug-log.txt)

    Returns:
        Configured root logger
    """
    if log_file is None:
        log_file = DEBUG_LOG_FILE

    # Create formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(name)-20s | %(message)s'
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything

    # Clear existing handlers
    root_logger.handlers = []

    # File handler - captures everything to debug-log.txt
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Console handler - shows info and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Log startup
    root_logger.info(f"Logging initialized - file: {log_file}")
    root_logger.debug(f"Debug logging enabled")

    return root_logger


def log_exception(exc: Exception, context: str = "") -> None:
    """
    Log an exception with full traceback.

    Args:
        exc: The exception to log
        context: Additional context about where the exception occurred
    """
    logger = logging.getLogger(__name__)

    tb = traceback.format_exc()

    if context:
        logger.error(f"Exception in {context}: {type(exc).__name__}: {exc}")
    else:
        logger.error(f"Exception: {type(exc).__name__}: {exc}")

    logger.debug(f"Full traceback:\n{tb}")


def log_startup_info() -> None:
    """Log system and environment information at startup."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("MetaMindIQTrain - Startup")
    logger.info("=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Debug log: {DEBUG_LOG_FILE}")
    logger.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (use __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LogCapture:
    """Context manager to capture log output for testing."""

    def __init__(self, logger_name: str = None, level: int = logging.DEBUG):
        self.logger_name = logger_name
        self.level = level
        self.handler = None
        self.records = []

    def __enter__(self):
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.records.append(record)
        self.handler.setLevel(self.level)

        if self.logger_name:
            logger = logging.getLogger(self.logger_name)
        else:
            logger = logging.getLogger()

        logger.addHandler(self.handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.logger_name:
            logger = logging.getLogger(self.logger_name)
        else:
            logger = logging.getLogger()

        logger.removeHandler(self.handler)
        return False

    def get_messages(self) -> list:
        """Get captured log messages."""
        return [record.getMessage() for record in self.records]

    def has_error(self) -> bool:
        """Check if any errors were logged."""
        return any(r.levelno >= logging.ERROR for r in self.records)

    def has_warning(self) -> bool:
        """Check if any warnings were logged."""
        return any(r.levelno >= logging.WARNING for r in self.records)


# Initialize logging when module is imported
_initialized = False

def ensure_logging() -> None:
    """Ensure logging is initialized."""
    global _initialized
    if not _initialized:
        setup_logging()
        _initialized = True


if __name__ == "__main__":
    # Test the logging system
    setup_logging()
    log_startup_info()

    logger = get_logger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(e, "test function")

    print(f"\nLog file written to: {DEBUG_LOG_FILE}")
