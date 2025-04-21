import logging
import sys
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel


class LoggingConfig(BaseModel):
    """Logging configuration to be set for the application"""

    LOGGER_NAME: str = "graphrag_pmqa"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: Optional[str] = "../logs/graphrag_pmqa.log"
    ROTATION: str = "20 MB"
    RETENTION: str = "1 month"


logging_config = LoggingConfig()


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    Configure logging for the application.
    """
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Remove all the default handlers
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=logging_config.LOG_FORMAT,
        level=logging_config.LOG_LEVEL,
        enqueue=True,
    )
    
    # Add file handler if configured
    if logging_config.LOG_FILE_PATH:
        logger.add(
            logging_config.LOG_FILE_PATH,
            format=logging_config.LOG_FORMAT,
            level=logging_config.LOG_LEVEL,
            rotation=logging_config.ROTATION,
            retention=logging_config.RETENTION,
            enqueue=True,
        )
    
    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    
    # Remove every other logger's handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    
    # Configure loguru
    logger.configure(handlers=[{"sink": sys.stdout, "level": logging_config.LOG_LEVEL}])
    
    logger.info("Logging configured successfully")
