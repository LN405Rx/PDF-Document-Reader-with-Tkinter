"""
Logging configuration for the PDF to Audiobook converter
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Configure and return a logger with rotating file handler and console handler
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Rotating file handler (10MB per file, max 5 files)
    log_file = log_dir / f"audiobook_player_{datetime.now().strftime('%Y%m')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
