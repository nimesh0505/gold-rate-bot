import logging
from datetime import datetime

def setup_logger() -> logging.Logger:
    """Set up structured logger with timestamp and log level."""
    logger = logging.getLogger("gold_rate_bot")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
