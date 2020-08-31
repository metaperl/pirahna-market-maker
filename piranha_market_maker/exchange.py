import ccxt
from settings import settings
from loguru import logger

def factory(exchange_str):
    exchange_str = exchange_str.lower()
    exchange_class = getattr(ccxt, exchange_str)
    exchange_settings = getattr(settings.exchange, exchange_str)
    logger.debug(f"{exchange_settings=}")
    args = {
        'apiKey': exchange_settings.api_key,
        'secret': exchange_settings.api_secret,
    }
    logger.debug(f"args to ccxt={args}")
    exchange = exchange_class(args)
    logger.debug(f"{exchange=}")
    return exchange
