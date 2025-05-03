"""
Webhook Endpoint for Telegram Bot

This module defines the FastAPI endpoint that receives webhook updates from Telegram
and forwards them to the bot's dispatcher for processing.
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from aiogram.types import Update
import json
from app.bot.bot_instance import application
from app.utils.redact import sanitize_user_data
from app.core.config import settings

router = APIRouter()

@router.post("")
async def telegram_webhook(request: Request):
    """
    Endpoint for receiving webhook updates from Telegram.

    This endpoint accepts POST requests from Telegram containing updates,
    and passes them to the appropriate handlers via the dispatcher.
    """
    # Get the update data from the request
    update_data = await request.json()

    # Convert the data to an Update object
    telegram_update = Update.model_validate(update_data)

    # Log update type for debugging (with sensitive information removed)
    import logging
    logger = logging.getLogger(__name__)

    # Get JSON representation of the update
    update_json = telegram_update.model_dump_json(exclude_none=True)
    update_dict = json.loads(update_json)

    # Sanitize the update data
    sanitized_update = sanitize_user_data(update_dict)

    # Log sanitized update
    logger.info(f"Received update: {json.dumps(sanitized_update)}")

    try:
        # Log command information for debugging
        if telegram_update.message and telegram_update.message.text and telegram_update.message.text.startswith('/'):
            command_text = telegram_update.message.text.split()[0]
            logger.info(f"Received command: {command_text} from user: [REDACTED_ID]")

            # Log entity information if available
            if telegram_update.message.entities:
                for entity in telegram_update.message.entities:
                    logger.info(f"Entity: {entity.type} at offset {entity.offset}, length {entity.length}")

        # Process the update with aiogram v3 style
        await application["dispatcher"].feed_update(
            bot=application["bot"],
            update=telegram_update
        )

        # Note: We've removed the fallback mechanism because it was causing duplicate messages.
        # The aiogram dispatcher is already handling the commands correctly.
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)

    # Return a success response
    return {"status": "success"}
