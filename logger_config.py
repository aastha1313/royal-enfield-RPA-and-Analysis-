import logging
import os
from datetime import datetime

def setup_logger():
    # Create logs folder if not exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"logs/run_{timestamp}.log"

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers (IMPORTANT)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Log file created: {log_file}")

    return logger