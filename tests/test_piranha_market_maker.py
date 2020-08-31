from piranha_market_maker import __version__
from piranha_market_maker.piranha_market_maker import Requests


def test_connect():
    r = Requests()
    print("---------------------", r.exchange, r)
    # print(f"Markets={r.exchange.load_markets()}")
    print(f"Balance={r.exchange.fetch_balance()}")
    assert __version__ == '0.2.0'
