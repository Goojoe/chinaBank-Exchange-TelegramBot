"""
Error handling utilities for the Exchange Rate Bot.

This module provides custom exceptions and error handling utilities for
gracefully handling errors throughout the application and generating
user-friendly error messages for Telegram responses.
"""
import logging
from typing import Optional, Callable, Any, TypeVar, Coroutine

from aiogram import types

logger = logging.getLogger(__name__)

# Type definitions for better type hinting with async functions
T = TypeVar('T')
AsyncFunction = Callable[..., Coroutine[Any, Any, T]]


# Custom exceptions
class ExchangeRateError(Exception):
    """Base exception for all exchange rate related errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NetworkError(ExchangeRateError):
    """Exception raised for network-related errors."""

    def __init__(self, message: str = "Network error occurred", original_error: Optional[Exception] = None):
        self.original_error = original_error
        if original_error:
            message = f"{message}: {str(original_error)}"
        super().__init__(message)


class ParsingError(ExchangeRateError):
    """Exception raised for errors in parsing exchange rate data."""

    def __init__(self, message: str = "Error parsing exchange rate data", original_error: Optional[Exception] = None):
        self.original_error = original_error
        if original_error:
            message = f"{message}: {str(original_error)}"
        super().__init__(message)


class RateNotFoundError(ExchangeRateError):
    """Exception raised when a requested exchange rate is not found."""

    def __init__(self, from_currency: str, to_currency: str):
        message = f"Exchange rate not found for {from_currency} to {to_currency}"
        super().__init__(message)


class InvalidCurrencyError(ExchangeRateError):
    """Exception raised for invalid currency codes."""

    def __init__(self, currency_code: str):
        message = f"Invalid currency code: {currency_code}"
        super().__init__(message)


class InvalidAmountError(ExchangeRateError):
    """Exception raised for invalid amount inputs."""

    def __init__(self, amount: str):
        message = f"Invalid amount value: {amount}"
        super().__init__(message)


# Error handling utilities
def format_error_message(error: Exception) -> str:
    """
    Format an exception into a user-friendly error message for Telegram.

    Args:
        error: The exception to format

    Returns:
        A formatted error message string
    """
    if isinstance(error, RateNotFoundError):
        return f"❌ {error.message}. Please check the currency codes and try again."

    elif isinstance(error, InvalidCurrencyError):
        return f"❌ {error.message}. Please use a valid currency code (e.g., USD, EUR, CNY)."

    elif isinstance(error, InvalidAmountError):
        return f"❌ {error.message}. Please enter a valid number."

    elif isinstance(error, NetworkError):
        return f"❌ Network error: Unable to fetch exchange rate data. Please try again later."

    elif isinstance(error, ParsingError):
        return f"❌ Error processing exchange rate data. Please try again later."

    elif isinstance(error, ExchangeRateError):
        return f"❌ {error.message}"

    # Generic error handling
    return f"❌ An error occurred: {str(error)}"


async def handle_exchange_rate_error(error: Exception, message: types.Message) -> None:
    """
    Handle an exchange rate error by logging it and sending an error message to the user.

    Args:
        error: The exception to handle
        message: The Telegram message to respond to
    """
    error_message = format_error_message(error)
    logger.error(f"Exchange rate error: {str(error)}")
    await message.answer(error_message)


async def safe_execution(
    func: AsyncFunction[T],
    message: types.Message,
    *args, **kwargs
) -> Optional[T]:
    """
    Execute a function safely with error handling.

    Args:
        func: The async function to execute
        message: The Telegram message to respond to if an error occurs
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function, or None if an error occurred
    """
    try:
        return await func(*args, **kwargs)
    except ValueError as e:
        if "amount" in str(e).lower():
            await handle_exchange_rate_error(InvalidAmountError(str(e)), message)
        else:
            await handle_exchange_rate_error(e, message)
    except ExchangeRateError as e:
        await handle_exchange_rate_error(e, message)
    except Exception as e:
        logger.exception(f"Unexpected error in {func.__name__}: {e}")
        await handle_exchange_rate_error(e, message)

    return None


def validate_currency_code(currency_code: str) -> str:
    """
    Validate a currency code format.

    Args:
        currency_code: The currency code to validate

    Returns:
        The validated currency code (uppercase)

    Raises:
        InvalidCurrencyError: If the currency code is invalid
    """
    code = currency_code.strip().upper()

    # Basic validation: Most currency codes are 3 letters
    if not code or not code.isalpha() or len(code) != 3:
        raise InvalidCurrencyError(currency_code)

    return code


def validate_amount(amount_str: str) -> float:
    """
    Validate and convert an amount string to a float.

    Args:
        amount_str: The amount string to validate

    Returns:
        The validated amount as a float

    Raises:
        InvalidAmountError: If the amount is invalid
    """
    try:
        amount = float(amount_str)

        if amount <= 0:
            raise InvalidAmountError(amount_str)

        return amount
    except ValueError:
        raise InvalidAmountError(amount_str)
