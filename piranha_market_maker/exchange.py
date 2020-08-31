import ccxt
from settings import settings
from loguru import logger
import piranha_market_maker.util as u

def factory(exchange_str):
    exchange_str = exchange_str.lower()
    exchange_class = getattr(ccxt, exchange_str)
    exchange_settings = getattr(settings.exchange, exchange_str)
    logger.debug(f"{exchange_settings=}")
    args = {
        'apiKey': exchange_settings.api_key,
        'secret': exchange_settings.secret,
    }
    logger.debug(f"args to ccxt={args}")
    exchange = exchange_class(args)
    logger.debug(f"{exchange=}")
    logger.debug(f"{u.pretty_dump('Markets', exchange.load_markets())}")
    logger.debug(f"{u.pretty_dump('Methods', dir(exchange))}")
    return exchange
