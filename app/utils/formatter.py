"""
Formatter for exchange rate data.

This module provides functions to format exchange rate data into user-friendly strings
for Telegram messages.
"""
from typing import Dict, Any, List, Optional


def format_exchange_rate(from_currency: str, to_currency: str, rate: float) -> str:
    """
    Format a single exchange rate into a user-friendly string.

    Args:
        from_currency: The source currency code (e.g., "USD")
        to_currency: The target currency code (e.g., "EUR")
        rate: The exchange rate value

    Returns:
        A formatted string representing the exchange rate
    """
    return (
        f"📊 Current exchange rate:\n"
        f"1 {from_currency} = {rate:.4f} {to_currency}"
    )


def format_currency_conversion(
    from_currency: str,
    to_currency: str,
    amount: float,
    rate: float
) -> str:
    """
    Format a currency conversion result into a user-friendly string.

    Args:
        from_currency: The source currency code (e.g., "USD")
        to_currency: The target currency code (e.g., "EUR")
        amount: The amount to convert
        rate: The exchange rate value

    Returns:
        A formatted string representing the conversion result
    """
    converted_amount = amount * rate
    return (
        f"💱 Currency conversion:\n"
        f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}\n"
        f"(Rate: 1 {from_currency} = {rate:.4f} {to_currency})"
    )


def format_cny_conversion(
    from_currency: str,
    amount: float,
    rate: float
) -> str:
    """
    Format a conversion to CNY into a user-friendly string.

    Args:
        from_currency: The source currency code (e.g., "USD")
        amount: The amount to convert
        rate: The exchange rate value

    Returns:
        A formatted string representing the conversion to CNY
    """
    converted_amount = amount * rate
    return (
        f"💱 Conversion to RMB:\n"
        f"{amount:.2f} {from_currency} = {converted_amount:.2f} CNY\n"
        f"(Rate: 1 {from_currency} = {rate:.4f} CNY)"
    )


def format_currency_list(currencies: List[str]) -> str:
    """
    Format a list of currencies into a user-friendly string.

    Args:
        currencies: List of currency strings (e.g., ["USD - US Dollar", "EUR - Euro"])

    Returns:
        A formatted string representing the list of currencies
    """
    currency_list = "\n".join(currencies)
    return (
        f"💰 Supported currencies:\n\n{currency_list}\n\n"
        "Use /rate or /convert to get rates and convert currencies."
    )


def format_rate_data(rate_data: Dict[str, Any], base_currency: Optional[str] = None) -> str:
    """
    Format the complete exchange rate data into a user-friendly string.

    Args:
        rate_data: Dictionary containing the parsed exchange rate data
        base_currency: Optional base currency to highlight (e.g., "USD")

    Returns:
        A formatted string representing the complete exchange rate data
    """
    if not rate_data or "currencies" not in rate_data or not rate_data["currencies"]:
        return "No exchange rate data available."

    currencies = rate_data["currencies"]
    last_updated = rate_data.get("last_updated", "Unknown")

    # Format the header
    result = f"📈 Exchange Rates\n"
    if last_updated:
        result += f"Last Updated: {last_updated}\n\n"
    else:
        result += "\n"

    # If base currency is provided, format rates relative to it
    if base_currency and base_currency in currencies:
        base_rate = currencies[base_currency]
        result += f"Base Currency: {base_currency}\n\n"

        for code, rate in sorted(currencies.items()):
            if code != base_currency:
                relative_rate = rate / base_rate
                result += f"1 {base_currency} = {relative_rate:.4f} {code}\n"

    # Otherwise, just list all available rates
    else:
        for code, rate in sorted(currencies.items()):
            result += f"{code}: {rate:.4f}\n"

    return result
