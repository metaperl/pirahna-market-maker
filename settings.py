from pydantic import BaseModel, BaseSettings


def minutes(x):
    return x * 60


class EndPointModel(BaseModel):
    http = ''
    ws = ''


class Live(EndPointModel):
    http = 'https://api.phemex.com'
    ws = 'wss://phemex.com/ws'


class Test(EndPointModel):
    http = ' https://testnet-api.phemex.com'
    ws = 'wss://testnet.phemex.com/ws'


class EndPoint(BaseModel):
    live = Live()
    test = Test()


class Phemex(BaseModel):
    """
    Interface to Phemex API.

    Documented at https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md
    """
    api_key = ''
    secret = ''
    endpoint = EndPoint()


class Trading(BaseModel):
    pair = "BTC/USD"
    wallet_coin = 'BTC'
    number_of_orders = 5  # maximum is 50
    spread = 200  # in USD
    margin = 10  # multiplier of capital - https://github.com/verata-veritatis/bybit-market-maker/issues/5
    use = 0.5  # How much of capital to use

    order_reset_time = minutes(5)  # in seconds


class Exchange(BaseModel):
    phemex = Phemex()


class Settings(BaseSettings):
    exchange_label = 'Bitmex'

    exchange: Exchange = Exchange()
    trading: Trading = Trading()

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
