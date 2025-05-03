"""
Core configuration package for the application.

This package contains core configuration modules:
- config: Environment variables and application settings
- logging_conf: Logging configuration and setup
"""

from app.core.config import settings
from app.core.logging_conf import logger

__all__ = ["settings", "logger"]
