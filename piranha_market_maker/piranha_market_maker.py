# -*- coding: utf-8 -*-

'''

'''

import time

# Import settings.py
from settings import settings

from loguru import logger
from piranha_market_maker import exchange
import piranha_market_maker.util as u

ORDER_RESET_TIME = settings.trading.order_reset_time
TICKER = settings.trading.pair

def pretty_dump(o):
    import pprint
    return pprint.pformat(o, indent=4)

class Requests:

    def __init__(self):

        self.exchange = exchange.factory(settings.exchange_label)
        logger.debug(f"{self.exchange=}")

    def place_initial_orders(self, last_price, prices, quantity):
        responses = []
        self.set_to_cross()
        for price in prices:
            if price > last_price:
                side = 'sell'
            else:
                side = 'buy'
            responses.append(self.exchange.ccxt.create_order(
                symbol=settings.trading.pair,
                type='limit',
                side=side,
                amount=quantity,
                price=price
            ))
        return responses

    def place_closing_orders(self, side, prices, quantity):
        responses = []
        for price in prices:
            responses.append(self.exchange.ccxt.place_active_order(
                symbol=TICKER,
                order_type='limit',
                side=side,
                amount=quantity,
                price=price,
            ))
        return responses

    def close_position(self):
        return self.session.close_position(TICKER)

    def cancel_all(self):
        return self.session.cancel_all_active_orders(TICKER)

    def get_wallet_balance(self):
        return self.exchange.free_coin(settings.trading.wallet_coin)


    def get_position(self):
        open_orders = self.exchange.ccxt.fetch_open_orders(settings.trading.pair)
        logger.debug(f"{u.pretty_dump('OpenOrders', open_orders)}")
        return open_orders

    def get_last_price(self):
        t = self.exchange.ccxt.fetch_ticker(settings.trading.pair)
        logger.debug(f"{u.pretty_dump('Ticker', t)}")
        return t['last']

    def ping(self):
        return self.ws.ping()

    def set_to_cross(self):
        pass
        # return self.session.change_user_leverage(TICKER, 0)

    def set_stop_loss(self):
        self.session.set_trading_stop(TICKER,
                                      stop_loss=self.get_position()[TICKER]['entry_price'])

    def _test_sub(self):
        return self.ws.fetch(f'instrument_info.100ms.{TICKER}')


class Algorithm:

    def __init__(self):
        self.req = Requests()

    def submit_initial(self):

        SPREAD = settings.trading.spread
        NUM_OF_ORDERS = settings.trading.number_of_orders
        MARGIN = settings.trading.margin
        USE = settings.trading.use

        # Determine last price.
        last_price = self.req.get_last_price()

        # Set the minimum and maximum of the range.
        max_p = last_price + SPREAD / 2
        min_p = last_price - SPREAD / 2

        # Determine the interval.
        interval = (max_p - min_p) / (NUM_OF_ORDERS - 1)

        # Scale the prices.
        prices = [max_p - interval * i for i in range(NUM_OF_ORDERS - 1)]
        prices.append(min_p)

        # Determine the margin per order.
        # 1st determine amount of capital we have to play with
        balance = self.req.get_wallet_balance() * last_price * MARGIN * USE
        # Divide the capital into orders
        quantity = balance / NUM_OF_ORDERS

        # Set initial orders.
        responses = self.req.place_initial_orders(last_price, prices, quantity)
        logger.debug(f"{responses=}")

        # Return last price.
        return last_price, interval, quantity

    def submit_closing(self, median, interval, qty):

        p_req = self.req.get_position()
        if p_req != []:
            position = p_req[TICKER]['size']
        else:
            self.req.cancel_all();
            self.req.close_position()
            raise Exception('Can\'t obtain position size.')

        if p_req[TICKER]['side'] == 'Buy':
            side = 'Sell'
        elif p_req[TICKER]['side'] == 'Sell':
            side = 'Buy'
            interval = -interval

        num_filled = round(position / qty)

        prices = [median + interval * (i + 1) for i in range(num_filled)]

        return self.req.place_closing_orders(side, prices, qty)

    def run(self):

        # Close any initial position.
        try:
            if len(self.req.get_position()) > 0:
                self.req.close_position()
        except KeyError:
            pass

        # Set initial booleans.
        orders_set = False
        closing = False

        while True:

            # Reset booleans
            if closing:
                orders_set = False
                closing = False

            # Place initial orders.
            if not orders_set:
                median, interval, qty = self.submit_initial()
                set_time = time.time()
                orders_set = True


            # Wait for position.
            position = self.req.get_position()



            # If we haven't received any position data yet, handle it.
            # try:
            #     position[TICKER]['size']
            # except KeyError:
            #     position = {};
            #     position[TICKER]['size'] = 0

            # While we are in a position...
            while len(position) > 0:

                logger.debug(f"{median=}, {closing=}, {last=}")

                # If we're not trying to close yet.
                if not closing:

                    # Reload last price.
                    last = self.req.get_last_price()
                    logger.debug(f"Last price={last}. {median=}")

                #     # If we're in position and we cross back over the median.
                #     if ((position[TICKER]['side'] == 'Buy' and last > median) or
                #             (position[TICKER]['side'] == 'Sell' and last < median)):
                #         # Cancel all orders and set stop loss at B.E.
                #         self.req.cancel_all()
                #         self.req.set_stop_loss()
                #
                #         # Set close orders and set boolean to True.
                #         self.submit_closing(median, interval, qty)
                #         closing = True
                #
                # # Reload position.
                position = self.req.get_position()

                # Sleep for a second.
                time.sleep(1)

            # If we're waited until reset time without fills, retry.
            if (time.time() - set_time > ORDER_RESET_TIME and not closing and
                    orders_set and len(position) == 0):
                # Cancel and retry.
                self.req.cancel_all()
                orders_set = False

            # Sleep for three seconds.
            time.sleep(3)


class Application:
    def __init__(self):
        Algorithm().run()
