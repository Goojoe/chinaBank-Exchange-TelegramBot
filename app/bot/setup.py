"""
Bot setup and initialization functions.

This module contains functions for setting up the Telegram webhook
and initializing the application with required data.
"""
import logging
from typing import Dict, Any

from app.bot.bot_instance import bot
from app.core.config import settings
from app.services.exchange_rate import fetch_and_parse_rate_data

logger = logging.getLogger(__name__)

# Cache for storing pre-loaded exchange rate data
_exchange_rate_cache: Dict[str, Any] = {}

async def set_telegram_webhook() -> bool:
    """
    Set the Telegram webhook URL for receiving updates.

    Returns:
        bool: True if webhook was set successfully, False otherwise
    """
    try:
        # Combine base URL with webhook path
        full_webhook_url = f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}"
        logger.info(f"Setting Telegram webhook to {full_webhook_url}")
        await bot.set_webhook(url=full_webhook_url)
        logger.info("Telegram webhook set successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to set Telegram webhook: {e}")
        return False

async def _preload_exchange_rate_data() -> None:
    """
    Preload exchange rate data to avoid delays during user requests.
    """
    try:
        # Use the URL from settings
        url = settings.BOC_URL
        logger.info(f"Preloading exchange rate data from {url}")

        # Fetch the exchange rate data
        data = await fetch_and_parse_rate_data(url)

        if data and "currencies" in data:
            global _exchange_rate_cache
            _exchange_rate_cache = data
            logger.info(f"Successfully preloaded exchange rate data for {len(data.get('currencies', {}))} currencies")
            logger.debug(f"Currencies available: {', '.join(data.get('currencies', {}).keys())}")
            logger.debug(f"Last updated: {data.get('last_updated', 'N/A')}")
        else:
            logger.warning("Preloaded exchange rate data is empty or invalid")
    except Exception as e:
        logger.error(f"Error preloading exchange rate data: {e}")

# Make the exchange rate data accessible to other modules
def get_cached_exchange_data():
    """
    Get the cached exchange rate data.

    Returns:
        dict: The cached exchange rate data
    """
    return _exchange_rate_cache

async def initialize_app() -> None:
    """
    Initialize the application with required data and services.

    This function performs any initial data loading or service setup
    required before the application can handle requests.
    """
    from app.bot.bot_instance import dp, application
    from app.bot.handlers import register_handlers

    # Ensure handlers are registered
    logger.info("Registering bot command handlers")
    register_handlers()

    # Just log the count of registered handlers instead of all details
    logger.info(f"Command handlers registered successfully")
    # For debugging only, enable when needed
    logger.debug(f"Dispatcher routes: {dp.message.handlers}")

    # We don't want to use polling with webhook mode
    logger.info("Bot using webhook mode only - not starting polling")

    # Set the webhook
    webhook_result = await set_telegram_webhook()

    if not webhook_result:
        logger.warning("Application started with webhook configuration issues")

    # Preload exchange rate data
    await _preload_exchange_rate_data()

    # Additional initialization tasks can be added here

    logger.info("Application initialization completed")

async def cleanup_app() -> None:
    """
    Perform cleanup tasks when the application is shutting down.

    This function handles any necessary cleanup before the application exits.
    """
    try:
        # Remove webhook on shutdown (optional, depending on your needs)
        # await bot.delete_webhook()

        logger.info("Application cleanup completed")
    except Exception as e:
        logger.error(f"Error during application cleanup: {e}")
