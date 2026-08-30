"""
Logging configuration for the Cricket Agent
Centralized logging setup for all modules
"""

import logging
import sys
from pathlib import Path

from config.settings import LOG_FILE, LOG_LEVEL, LOG_FORMAT


def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger for a specific module
    
    Args:
        name: Logger name (typically __name__ from the calling module)
    
    Returns:
        Configured logger instance
    
    Example:
        logger = setup_logger(__name__)
        logger.info("Scraper started")
        logger.error("Failed to fetch data")
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Formatter: timestamp, logger name, level, message
    formatter = logging.Formatter(LOG_FORMAT)
    
    # File handler: log to file
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler: log to terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Example of how to use in other modules:
# from src.logger_setup import setup_logger
# logger = setup_logger(__name__)
# logger.info("Starting scraper...")