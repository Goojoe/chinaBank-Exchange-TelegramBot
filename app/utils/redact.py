"""
User data redaction utilities

This module provides utility functions for redacting sensitive user information
in logs and other output.
"""
import logging
import json
import copy
from typing import Dict, Any, Union
from aiogram import types
from app.core.config import settings

logger = logging.getLogger(__name__)

def redact_user_info(message: types.Message) -> str:
    """
    Redact sensitive user information from a message object.
    Returns a string representation with user information redacted.

    Args:
        message: The message object to redact information from

    Returns:
        A string with sensitive information redacted
    """
    # Check if redaction is enabled
    if not settings.REDACT_USER_DATA:
        # If disabled, return basic info without redaction
        if hasattr(message, "from_user") and hasattr(message.from_user, "id"):
            user_id = message.from_user.id
        else:
            user_id = "unknown"
        return f"message from user {user_id}"

    # Create a basic info string (redacted version)
    info = "message"

    # Add message ID if available
    if hasattr(message, "message_id"):
        info += f" id={message.message_id}"

    # Add chat type if available
    if hasattr(message, "chat") and hasattr(message.chat, "type"):
        info += f" chat_type={message.chat.type}"

    # Add command text if available but don't include user arguments
    if hasattr(message, "text") and message.text and message.text.startswith('/'):
        command = message.text.split()[0]
        info += f" command={command}"

    return info

def log_command_safely(logger, command_name: str, message: types.Message) -> None:
    """
    Safely log command execution without exposing user information.

    Args:
        logger: The logger instance to use
        command_name: The name of the command being executed
        message: The message object containing the command
    """
    redacted_info = redact_user_info(message)
    logger.info(f"Handling {command_name} command - {redacted_info}")

def sanitize_user_data(update_data: Union[Dict[str, Any], Any]) -> Union[Dict[str, Any], Any]:
    """
    Sanitize user data by hiding first_name and user ID in the logs.
    This function can be used by both webhook.py and other handlers.

    Args:
        update_data: The update data to sanitize (dictionary or other object)

    Returns:
        A copy of the update data with sensitive information redacted
    """
    # If redaction is disabled, return the original data
    if not settings.REDACT_USER_DATA:
        return update_data

    # Make a deep copy to avoid modifying the original data
    sanitized_data = copy.deepcopy(update_data)

    # If update_data is not a dict, return it as is
    if not isinstance(sanitized_data, dict):
        return sanitized_data

    # Sanitize data in message
    if 'message' in sanitized_data and sanitized_data['message']:
        # Sanitize from_user in message
        if 'from_user' in sanitized_data['message'] and sanitized_data['message']['from_user']:
            if 'first_name' in sanitized_data['message']['from_user']:
                sanitized_data['message']['from_user']['first_name'] = '[REDACTED]'
            if 'id' in sanitized_data['message']['from_user']:
                sanitized_data['message']['from_user']['id'] = '[REDACTED_ID]'

        # Sanitize from in message (older format)
        if 'from' in sanitized_data['message'] and sanitized_data['message']['from']:
            if 'first_name' in sanitized_data['message']['from']:
                sanitized_data['message']['from']['first_name'] = '[REDACTED]'
            if 'id' in sanitized_data['message']['from']:
                sanitized_data['message']['from']['id'] = '[REDACTED_ID]'

        # Sanitize chat in message
        if 'chat' in sanitized_data['message'] and sanitized_data['message']['chat']:
            if 'first_name' in sanitized_data['message']['chat']:
                sanitized_data['message']['chat']['first_name'] = '[REDACTED]'
            if 'id' in sanitized_data['message']['chat']:
                sanitized_data['message']['chat']['id'] = '[REDACTED_CHAT_ID]'

    # Handle other update types if needed

    return sanitized_data
