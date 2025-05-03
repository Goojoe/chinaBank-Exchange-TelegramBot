import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


def setup_logging():
    """
    Configure application logging.

    Sets up formatters, handlers, and log levels for the application.
    """
    # Create logs directory one level up from the current directory
    # logs_dir = Path("../logs")
    # Check if directory exists and create it if not
    # if not logs_dir.exists():
    #     logs_dir.mkdir(exist_ok=True, parents=True)

    # Set up log formatters
    simple_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)

    # Set up file handler for all logs
    # file_handler = RotatingFileHandler(
    #     filename=logs_dir / "app.log",
    #     maxBytes=10485760,  # 10MB
    #     backupCount=5,
    #     encoding="utf-8"
    # )
    # file_handler.setFormatter(detailed_formatter)

    # Set up file handler for errors only
    # error_file_handler = RotatingFileHandler(
    #     filename=logs_dir / "error.log",
    #     maxBytes=10485760,  # 10MB
    #     backupCount=5,
    #     encoding="utf-8"
    # )
    # error_file_handler.setFormatter(detailed_formatter)
    # error_file_handler.setLevel(logging.ERROR)

    # Configure root logger
    root_logger = logging.getLogger()

    # Set log level based on debug mode
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    root_logger.setLevel(log_level)

    # Add handlers to the logger
    root_logger.addHandler(console_handler)
    # root_logger.addHandler(file_handler)
    # root_logger.addHandler(error_file_handler)

    # Configure third-party loggers (reduce noise)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Set exchange rate service to WARNING level to avoid excessive logging
    logging.getLogger("app.services.exchange_rate").setLevel(logging.WARNING)

    # Return configured root logger
    return root_logger


# Initialize logger
logger = setup_logging()
