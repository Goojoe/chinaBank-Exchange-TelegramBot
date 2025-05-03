"""
Telegram Bot Command Handlers

This module defines and registers command handlers for the Telegram bot.
Commands include: start, rate, convert, currency, cny_convert.
"""
from aiogram import types
from aiogram.filters import Command

from app.bot.bot_instance import application, dp
from app.services.exchange_rate import get_exchange_rate, fetch_and_parse_rate_data
from app.utils.redact import log_command_safely

# Command handler functions
async def start_command(message: types.Message, bot=None):
    """Handler for the /start command"""
    import os

    # Use bot parameter if provided, otherwise use message.bot
    bot_to_use = bot or message.bot

    # Read command descriptions from bot_commands.txt
    commands_file_path = os.path.join(os.getcwd(), "bot_commands.txt")
    commands_list = []

    try:
        with open(commands_file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    # Split each line into command and description
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        cmd, desc = parts
                        commands_list.append(f"/{cmd} - {desc}")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error reading bot_commands.txt: {e}")
        # Fallback to default message if file can't be read
        commands_list = [
            "/start - 启动消息",
            "/rate - 获取所有货币汇率",
            "/convert - 转换货币 举例 /convert usd eur 100",
            "/currency - 获取货币列表",
            "/cny_convert - 其他货币转换人民币 /cny_convert usd 100"
        ]

    commands_text = "\n".join(commands_list)

    await bot_to_use.send_message(
        chat_id=message.chat.id,
        text=f"👋 欢迎使用中国银行汇率机器人！\n\n"
        f"使用以下命令与我交互：\n"
        f"{commands_text}"
    )

async def rate_command(message: types.Message, bot=None):
    """Handler for the /rate command - displays exchange rates in simplified format"""
    import logging
    logger = logging.getLogger(__name__)
    from app.core.config import settings

    # Use bot parameter if provided, otherwise use message.bot
    bot_to_use = bot or message.bot

    try:
        # Get the URL from environment variable
        url = settings.BOC_URL

        # Fetch exchange rate data directly with cache info
        data, is_cached, next_update = await fetch_and_parse_rate_data(url)

        if not data or "currencies" not in data or not data["currencies"]:
            await bot_to_use.send_message(
                chat_id=message.chat.id,
                text="❌ 无法获取汇率数据，请稍后再试。"
            )
            return

        # Get the last updated time
        last_updated = data.get("last_updated", "未知")

        # Add cache status and next update time
        cache_status = "✅ 数据来源: 缓存" if is_cached else "🔄 数据来源: 实时获取"
        next_update_str = next_update.strftime("%Y-%m-%d %H:%M:%S")

        # Start response with update time header including the timestamp
        response_lines = [
            f"汇率更新时间\n{last_updated}\n",
            f"{cache_status}",
            f"下次更新时间: {next_update_str}\n"
        ]

        # Get supported currencies and their Chinese names
        supported_currencies = settings.SUPPORTED_CURRENCIES
        currency_names = settings.CURRENCY_NAMES

        # Dictionary with currency rates
        currencies_data = data["currencies"]

        # Map currencies to their rates in the simplified format
        for currency_code in supported_currencies:
            # Skip CNY itself
            if currency_code == "CNY":
                continue

            # Get Chinese name for the currency
            chinese_name = currency_names.get(currency_code, "")

            # Get rate directly from the data
            if currency_code in currencies_data:
                rate = currencies_data[currency_code]
                # Format as requested: 美元usd:730 (lowercase currency code)
                response_lines.append(f"{currency_code.upper()}:{rate} {chinese_name}")

        # Join all lines and send the response
        response_text = "\n".join(response_lines)
        logger.info(f"Sending rate response (without user details)")

        await bot_to_use.send_message(
            chat_id=message.chat.id,
            text=response_text
        )
    except Exception as e:
        logger.error(f"Error in rate_command: {e}")
        # No user info in error log
        await bot_to_use.send_message(
            chat_id=message.chat.id,
            text=f"❌ 获取汇率数据时出错: {str(e)}"
        )

async def convert_command(message: types.Message, bot=None):
    """Handler for the /convert command"""
    # Use bot parameter if provided, otherwise use message.bot
    bot_to_use = bot or message.bot

    args = message.text.split()

    # Check if correct number of arguments
    if len(args) < 4:
        await bot_to_use.send_message(
            chat_id=message.chat.id,
            text="❓ 请使用以下格式: /convert 源货币 目标货币 金额\n"
                 "例如: /convert USD EUR 100"
        )
        return

    try:
        from_currency = args[1].upper()
        to_currency = args[2].upper()
        amount = float(args[3])

        # Check if target currency is CNY, redirect to /cny_convert
        if to_currency == "CNY":
            await bot_to_use.send_message(
                chat_id=message.chat.id,
                text=f"ℹ️ 要将币种转换为人民币，请使用 /cny_convert 命令:\n"
                     f"/cny_convert {from_currency} {amount}"
            )
            return

        rate_info = await get_exchange_rate(from_currency, to_currency)
        rate, is_cached, next_update = rate_info

        if rate:
            # Get the last updated time
            from app.services.exchange_rate import fetch_and_parse_rate_data
            from app.core.config import settings

            # Fetch data to get the update time
            data, _, _ = await fetch_and_parse_rate_data(settings.BOC_URL)
            last_updated = data.get("last_updated", "未知")

            # Add cache status and next update time
            cache_status = "✅ 数据来源: 缓存" if is_cached else "🔄 数据来源: 实时获取"
            next_update_str = next_update.strftime("%Y-%m-%d %H:%M:%S")

            converted_amount = amount * rate
            await bot_to_use.send_message(
                chat_id=message.chat.id,
                text=f"💱 货币转换结果:\n"
                     f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}\n"
                     f"(汇率: 1 {from_currency} = {rate:.4f} {to_currency})\n\n"
                     f"汇率更新时间\n{last_updated}\n"
                     f"{cache_status}\n"
                     f"下次更新时间: {next_update_str}"
            )
        else:
            await bot_to_use.send_message(
                chat_id=message.chat.id,
                text=f"❌ 抱歉，无法将 {from_currency} 兑换为 {to_currency}。\n"
                     f"请检查货币代码并重试。"
            )
    except ValueError:
        await bot_to_use.send_message(
            chat_id=message.chat.id,
            text="❌ 金额无效。请输入有效的数字。"
        )
    except Exception as e:
        # Log error without user information
        logger = logging.getLogger(__name__)
        logger.error(f"Error in convert_command: {e}")

        await bot_to_use.send_message(
            chat_id=message.chat.id,
            text=f"❌ 发生错误: {str(e)}"
        )

async def currency_command(message: types.Message, bot=None):
    """Handler for the /currency command"""
    # Use bot parameter if provided, otherwise use message.bot
    bot_to_use = bot or message.bot

    # Get supported currencies from settings
    from app.core.config import settings
    supported_currencies = settings.SUPPORTED_CURRENCIES
    currency_names = settings.CURRENCY_NAMES

    # Create a list of currencies with their Chinese names
    currencies = []
    for code in supported_currencies:
        chinese_name = currency_names.get(code, "")
        currencies.append(f"{code} - {chinese_name}")

    currency_list = "\n".join(currencies)

    # Get the last updated time
    from app.services.exchange_rate import fetch_and_parse_rate_data
    from app.core.config import settings

    # Fetch data to get the update time
    data, is_cached, next_update = await fetch_and_parse_rate_data(settings.BOC_URL)
    last_updated = data.get("last_updated", "未知")

    # Add cache status and next update time
    cache_status = "✅ 数据来源: 缓存" if is_cached else "🔄 数据来源: 实时获取"
    next_update_str = next_update.strftime("%Y-%m-%d %H:%M:%S")

    await bot_to_use.send_message(
        chat_id=message.chat.id,
        text=f"💰 支持的货币列表:\n{currency_list}\n\n"
             f"使用 /rate 或 /convert 或 /cny_convert 获取汇率和转换货币。\n\n"
             f"汇率更新时间\n{last_updated}\n"
             f"{cache_status}\n"
             f"下次更新时间: {next_update_str}"
    )

async def cny_convert_command(message: types.Message, bot=None):
    """Handler for the /cny_convert command"""
    # Use bot parameter if provided, otherwise use message.bot
    bot_to_use = bot or message.bot

    args = message.text.split()

    # Check if correct number of arguments
    if len(args) < 3:
        await bot_to_use.send_message(
            chat_id=message.chat.id,
            text="❓ 请使用以下格式: /cny_convert 源货币 金额\n"
                 "例如: /cny_convert USD 100"
        )
        return

    try:
        from_currency = args[1].upper()
        amount = float(args[2])
        to_currency = "CNY"

        rate_info = await get_exchange_rate(from_currency, to_currency)
        rate, is_cached, next_update = rate_info

        if rate:
            # Get the last updated time
            from app.services.exchange_rate import fetch_and_parse_rate_data
            from app.core.config import settings

            # Fetch data to get the update time
            data, _, _ = await fetch_and_parse_rate_data(settings.BOC_URL)
            last_updated = data.get("last_updated", "未知")

            # Add cache status and next update time
            cache_status = "✅ 数据来源: 缓存" if is_cached else "🔄 数据来源: 实时获取"
            next_update_str = next_update.strftime("%Y-%m-%d %H:%M:%S")

            converted_amount = amount * rate
            await bot_to_use.send_message(
                chat_id=message.chat.id,
                text=f"💱 转换为人民币结果:\n"
                     f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}\n"
                     f"(汇率: 1 {from_currency} = {rate:.4f} {to_currency})\n\n"
                     f"汇率更新时间\n{last_updated}\n"
                     f"{cache_status}\n"
                     f"下次更新时间: {next_update_str}"
            )
        else:
            await bot_to_use.send_message(
                chat_id=message.chat.id,
                text=f"❌ 抱歉，无法将 {from_currency} 转换为人民币。\n"
                     f"请检查货币代码并重试。"
            )
    except ValueError:
        await bot_to_use.send_message(
            chat_id=message.chat.id,
            text="❌ 金额无效。请输入有效的数字。"
        )
    except Exception as e:
        # Log error without user information
        logger = logging.getLogger(__name__)
        logger.error(f"Error in cny_convert_command: {e}")

        await bot_to_use.send_message(
            chat_id=message.chat.id,
            text=f"❌ 发生错误: {str(e)}"
        )

# Register command handlers with the dispatcher
def register_handlers():
    # Register handlers with more detailed logging
    logger.info("Registering command handlers with dispatcher...")

    # Directly register handlers using decorator style as an alternative approach
    @dp.message(Command(commands=["start"]))
    async def start_handler(message: types.Message):
        log_command_safely(logger, "/start", message)
        await start_command(message)

    @dp.message(Command(commands=["rate"]))
    async def rate_handler(message: types.Message):
        log_command_safely(logger, "/rate", message)
        await rate_command(message)

    @dp.message(Command(commands=["convert"]))
    async def convert_handler(message: types.Message):
        log_command_safely(logger, "/convert", message)
        await convert_command(message)

    @dp.message(Command(commands=["currency"]))
    async def currency_handler(message: types.Message):
        log_command_safely(logger, "/currency", message)
        await currency_command(message)

    @dp.message(Command(commands=["cny_convert"]))
    async def cny_convert_handler(message: types.Message):
        log_command_safely(logger, "/cny_convert", message)
        await cny_convert_command(message)

    logger.info("All command handlers registered successfully")

# Debug message for imports
import logging
logger = logging.getLogger(__name__)
logger.info(f"Handlers module imported. Commands available: /start, /rate, /convert, /currency, /cny_convert")
# Note: Handlers are now registered via setup.py and not automatically here
