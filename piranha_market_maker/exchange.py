import ccxt
import ccxt.base.exchange

from settings import settings
from loguru import logger
import piranha_market_maker.util as u
from traitlets import HasTraits, default
import traitlets
import typing


def factory(exchange_str):
    exchange_class = globals()[exchange_str]

    exchange_str = exchange_str.lower()
    exchange_settings = getattr(settings.exchange, exchange_str)
    logger.debug(f"{exchange_settings=}")
    args = {
        'apiKey': exchange_settings.api_key,
        'secret': exchange_settings.secret,
    }
    logger.debug(f"args to ccxt={args}")
    exchange = exchange_class(ccxt_args=args)
    logger.debug(f"{exchange=}")
    logger.debug(f"{u.pretty_dump('Markets', exchange.ccxt.load_markets())}")
    logger.debug(f"{u.pretty_dump('Methods', dir(exchange))}")
    return exchange


class Exchange(HasTraits):
    ccxt_args = traitlets.Dict()
    ccxt = ccxt.base.exchange.Exchange()

    def cancel_all_active_orders(self, ticker):
        open_orders = self.ccxt.fetch_open_orders(settings.trading.pair)
        for order in open_orders:
            self.ccxt.cancel_order(order['id'], ticker)


class Phemex(Exchange):

    @default('ccxt')
    def bind_ccxt(self):
        return ccxt.phemex(self.ccxt_args)

    def free_coin(self, currency):
        r = self.ccxt.fetch_balance()
        return r[currency]['free']
