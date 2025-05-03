import os
import time
from typing import Dict, List, Optional, Any
import pytz
from dotenv import load_dotenv


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv(".env", encoding="utf-8")

        # Telegram Bot Configuration
        self.TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

        # Webhook Configuration
        self.WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
        self.WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH")

        # Server Configuration
        self.APP_HOST = os.environ.get("APP_HOST")
        self.APP_PORT = int(os.environ.get("APP_PORT"))
        self.APP_WORKERS = int(os.environ.get("APP_WORKERS", "4"))
        self.DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")

        # Cache Configuration (in minutes)
        self.CACHE_TIMEOUT = int(os.environ.get("CACHE_TIMEOUT", "5") or "5")


        # External Service URLs
        self.BOC_URL = os.environ.get("BOC_URL")

        # Time Zone Configuration
        self.TIMEZONE = os.environ.get("TIMEZONE")

        # Privacy Configuration
        self.REDACT_USER_DATA = os.environ.get("REDACT_USER_DATA", "True").lower() in ("true", "1", "t")

        # Currency Configuration
        self.SUPPORTED_CURRENCIES = self._parse_list(os.environ.get("SUPPORTED_CURRENCIES", ""))
        self.CURRENCY_NAMES = self._parse_dict(os.environ.get("CURRENCY_NAMES", ""))

        # Process any other settings
        self._post_init()

    def _parse_list(self, value: str) -> List[str]:
        """Parse a comma-separated string into a list."""
        if not value:
            return []
        return value.split(",")

    def _parse_dict(self, value: str) -> Dict[str, str]:
        """Parse a comma-separated string of key:value pairs into a dictionary."""
        result = {}
        if not value:
            return result

        for item in value.split(","):
            if ":" in item:
                key, val = item.split(":", 1)
                result[key] = val
        return result

    def _post_init(self) -> None:
        """Post initialization processing."""
        # No additional processing needed since we handle parsing in __init__
        pass


# Configure timezone
def set_timezone():
    """Set the system timezone according to the configuration."""
    timezone = settings.TIMEZONE
    try:
        # Verify the timezone is valid
        if timezone in pytz.all_timezones:
            # Set environment variable for time functions
            os.environ["TZ"] = timezone
            # Apply the timezone change (works on Unix-like systems)
            try:
                time.tzset()
            except AttributeError:
                # Windows doesn't have time.tzset()
                pass
    except Exception as e:
        print(f"Error setting timezone: {e}")


# Create settings instance
settings = Settings()

# Set timezone at module import
set_timezone()
