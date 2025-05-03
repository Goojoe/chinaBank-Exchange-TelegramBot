"""
Telegram Bot Instance Configuration

This module initializes and configures the Telegram bot instance
using the aiogram library and application settings.
"""
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.core.config import settings

# Create Bot instance with token from settings
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

# Create Dispatcher for handling updates
dp = Dispatcher()

# Create a combined application object that can be imported elsewhere
# This makes the bot and dispatcher easy to import in processor and settings scripts
application = {
    "bot": bot,
    "dispatcher": dp
}

# Initialize with default parse mode for messages
bot.parse_mode = ParseMode.HTML

__all__ = ["bot", "dp", "application"]
