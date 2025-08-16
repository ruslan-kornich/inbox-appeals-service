import logging
import sys

from app.config.settings import settings

# Configure project-wide logger
logger = logging.getLogger(settings.SERVICE_NAME)
# Use DEBUG level if in DEBUG mode, otherwise INFO
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

# Clear existing handlers to avoid duplicates
if logger.hasHandlers():
    logger.handlers.clear()

# Formatter for log messages
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logger.level)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
