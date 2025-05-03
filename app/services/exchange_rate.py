"""
Exchange rate service for fetching and parsing currency exchange rate data.
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple, Union
import functools

import httpx
from bs4 import BeautifulSoup
from aiocache import cached, Cache, SimpleMemoryCache
from aiocache.serializers import PickleSerializer

logger = logging.getLogger(__name__)

# Get cache TTL from environment (in minutes, convert to seconds)
from app.core.config import Settings
settings = Settings()
# Default to 60 minutes (3600 seconds) if not specified
CACHE_TTL = int(getattr(settings, "CACHE_TTL_MINUTES", 10)) * 60

CACHE_TTL = int(getattr(settings, "CACHE_TTL_MINUTES", 10)) * 60

# Create a global cache to store timestamps
_cache_timestamps = {}
@cached(ttl=CACHE_TTL, cache=SimpleMemoryCache)
# Custom caching implementation to track cache status
async def fetch_and_parse_rate_data(url: str, timeout: int = 10) -> Tuple[Dict[str, Any], bool, datetime]:
    """
    Asynchronously fetches exchange rate data from the specified URL and parses it,
    with caching and cache status tracking.

    Args:
        url: The URL to fetch the exchange rate data from
        timeout: Request timeout in seconds

    Returns:
        Tuple containing:
        - Dictionary containing the parsed exchange rate data
        - Boolean indicating whether the result is from cache
        - Datetime object indicating when the cache will be updated next

    Raises:
        Exception: If there's an error during fetching or parsing the data
    """

    is_cached = False
    now = datetime.now()


    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Fetching exchange rate data from {url}")
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()  # Raise exception for HTTP errors


            soup = BeautifulSoup(response.text, 'lxml')


            exchange_data = _parse_exchange_rate_data(soup)

            if not exchange_data:
                logger.error("Failed to extract exchange rate data")
                raise ValueError("Could not extract exchange rate data from the response")

            logger.info(f"Successfully fetched and parsed exchange rate data: {exchange_data}")



            return exchange_data, None, None

    except httpx.TimeoutException:
        logger.error(f"Timeout error while fetching data from {url}")
        raise Exception(f"Request to {url} timed out after {timeout} seconds")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while fetching data from {url}: {e}")
        raise Exception(f"HTTP error: {e}")
    except httpx.RequestError as e:
        logger.error(f"Network error while fetching data from {url}: {e}")
        raise Exception(f"Network error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching or parsing data: {e}")
        raise Exception(f"Error fetching or parsing exchange rate data: {e}")

def _parse_exchange_rate_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Parse the exchange rate data from the BeautifulSoup object.

    Args:
        soup: BeautifulSoup object representing the HTML content

    Returns:
        Dictionary containing the parsed exchange rate data with the following structure:
        {
            "currencies": {
                "USD": 727.67,
                "EUR": 824.88,
                ...
            },
            "last_updated": "2025.05.02 20:58:58"
        }
    """
    try:
        # Get config for currency mapping
        from app.core.config import Settings
        settings = Settings()
        currency_names = settings.CURRENCY_NAMES

        # Create reverse mapping from Chinese name to currency code
        reverse_currency_map = {v: k for k, v in currency_names.items()}

        # Find the main table containing exchange rate data
        # Look for the nested table with exchange rates (bgcolor="#EAEAEA")
        tables = soup.find_all('table')
        table = None
        for t in tables:
            if t.get('bgcolor') == "#EAEAEA":
                table = t
                break

        if not table:
            logger.warning("Exchange rate table not found in the HTML")
            return {}

        # Extract data for various currencies
        currencies = {}

        # Process all rows in the table
        rows = table.find_all('tr')

        # Skip if no rows found
        if not rows:
            logger.warning("No rows found in exchange rate table")
            return {}

        # Get headers from the first row
        headers = [th.text.strip() for th in rows[0].find_all('th')] if rows else []

        # Find indices for the columns we need
        currency_idx = headers.index('Currency Name') if 'Currency Name' in headers else -1
        cash_selling_idx = headers.index('Cash Selling Rate') if 'Cash Selling Rate' in headers else -1
        time_idx = headers.index('Pub Time') if 'Pub Time' in headers else -1

        # Check if required columns exist
        if currency_idx == -1 or cash_selling_idx == -1 or time_idx == -1:
            logger.warning("Required columns not found in the table")
            return {}

        # Extract the publication time from the first data row (only once)
        pub_time = None

        # Skip the header row
        for row in rows[1:]:
            cells = row.find_all('td')

            # Skip if not enough cells
            if len(cells) <= max(currency_idx, cash_selling_idx):
                continue

            # Extract currency name
            currency_name = cells[currency_idx].text.strip()
            if not currency_name:
                continue

            # Extract publication time (only once if not already set)
            if pub_time is None and len(cells) > time_idx:
                pub_time = cells[time_idx].text.strip()

            # Extract cash selling rate and convert to float if possible
            rate_text = cells[cash_selling_idx].text.strip()
            if rate_text:
                try:
                    cash_selling_rate = float(rate_text)

                    # Store rate by both currency code and Chinese name if possible
                    # This way we can look up by either one
                    if currency_name in reverse_currency_map:
                        currency_code = reverse_currency_map[currency_name]
                        currencies[currency_code] = cash_selling_rate  # Store by code (USD)

                    currencies[currency_name] = cash_selling_rate  # Also store by name (美元)

                except ValueError:
                    logger.warning(f"Could not parse Cash Selling Rate for {currency_name}: {rate_text}")

        # CNY is handled separately in conversion calculations, no need to add it here

        logger.info(f"Parsed currencies: {currencies}")

        return {
            "currencies": currencies,
            "last_updated": pub_time
        }

    except Exception as e:
        logger.error(f"Error parsing exchange rate data: {e}")
        return {}

async def get_exchange_rate(from_currency: str, to_currency: str) -> Union[Tuple[Optional[float], bool, datetime], Optional[float]]:
    """
    Get the exchange rate between two currencies based on Cash Selling Rate.

    Args:
        from_currency: The source currency code (e.g., "USD")
        to_currency: The target currency code (e.g., "EUR")

    Returns:
        A tuple containing:
        - The exchange rate as a float, or None if the rate couldn't be retrieved
        - Boolean indicating whether the result is from cache
        - Datetime object indicating when the cache will be updated next
    """
    try:
        # Get the URL from environment variable
        from app.core.config import Settings
        settings = Settings()
        url = settings.BOC_URL

        data, is_cached, next_update = await fetch_and_parse_rate_data(url)

        # This logic will depend on the structure of your parsed data
        if "currencies" not in data or not data["currencies"]:
            logger.error("No currency data available")
            return None

        currencies = data["currencies"]

        # Convert currency codes to Chinese names using the mapping from settings
        currency_names = settings.CURRENCY_NAMES

        # Get Chinese names for the currencies
        from_currency_name = currency_names.get(from_currency)
        to_currency_name = currency_names.get(to_currency)

        if not from_currency_name or not to_currency_name:
            logger.error(f"Missing Chinese name mapping for {from_currency} or {to_currency}")
            return None

        logger.info(f"Converting from {from_currency} ({from_currency_name}) to {to_currency} ({to_currency_name})")

        # Special handling for CNY
        # If to_currency is CNY, we just need the from_currency rate
        if to_currency == "CNY":
            # Find the source currency rate
            if from_currency in currencies:
                from_rate = currencies[from_currency]
            elif from_currency_name in currencies:
                from_rate = currencies[from_currency_name]
            else:
                logger.error(f"Could not find rate for {from_currency}")
                return None

            # For CNY conversion, return the rate divided by 100
            # This is because rates are quoted as CNY per 100 foreign currency units
            return from_rate / 100, is_cached, next_update

        # If from_currency is CNY, we need to handle differently
        elif from_currency == "CNY":
            # Find the target currency rate
            if to_currency in currencies:
                to_rate = currencies[to_currency]
            elif to_currency_name in currencies:
                to_rate = currencies[to_currency_name]
            else:
                logger.error(f"Could not find rate for {to_currency}")
                return None

            # For converting from CNY, we need reciprocal of the rate divided by 100
            return 100 / to_rate, is_cached, next_update

        # Normal case - converting between two non-CNY currencies
        else:
            # Look for both currencies in the data
            # First try by currency code, then by Chinese name as fallback
            if from_currency in currencies:
                from_rate = currencies[from_currency]
            elif from_currency_name in currencies:
                from_rate = currencies[from_currency_name]
            else:
                logger.error(f"Could not find rate for {from_currency}")
                return None

            if to_currency in currencies:
                to_rate = currencies[to_currency]
            elif to_currency_name in currencies:
                to_rate = currencies[to_currency_name]
            else:
                logger.error(f"Could not find rate for {to_currency}")
                return None

            # Calculate exchange rate between the two currencies
            exchange_rate = to_rate / from_rate
            return exchange_rate, is_cached, next_update

        # Note: This code is unreachable due to the return statements above
        logger.error(f"Exchange rate not available for {from_currency} to {to_currency}")
        return None, is_cached, next_update

    except Exception as e:
        logger.error(f"Error getting exchange rate: {e}")
        logger.exception("Stack trace:")
        return None, False, datetime.now() + timedelta(seconds=CACHE_TTL)
