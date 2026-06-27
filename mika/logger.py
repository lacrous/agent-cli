"""Logging utilities for mika CLI."""

import logging
from pathlib import Path
from typing import Optional

from mika.config import get_logs_dir


def setup_logging(level: int = logging.INFO, log_file: Optional[Path] = None) -> logging.Logger:
    """Configure and return the mika logger."""
    logger = logging.getLogger("mika")
    logger.setLevel(level)

    # Prevent duplicate handlers if called multiple times.
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if log_file is None:
        log_file = get_logs_dir() / "mika.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
