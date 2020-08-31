from piranha_market_maker import __version__
from piranha_market_maker.piranha_market_maker import Requests, Application

import json

def pretty_dump(o):
    return json.dumps(o, indent=4)

def pretty_dump2(o):
    import pprint

    return pprint.pformat(o, indent=4)

def test_connect():
    r = Requests()
    print("---------------------", r.exchange, r)
    # print(f"Markets={r.exchange.load_markets()}")
    # print(f"Balance={pretty_dump2(r.exchange.fetch_balance())}")
    Application()

    assert __version__ == '0.2.0'
