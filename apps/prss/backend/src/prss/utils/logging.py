"""Logging configuration"""
import logging
import json
from pythonjsonlogger import jsonlogger
from prss.config import settings


def setup_logging():
    """Setup JSON logging"""
    logger = logging.getLogger()
    handler = logging.StreamHandler()

    if settings.log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, settings.log_level))

    return logger
