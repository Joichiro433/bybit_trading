import time
from typing import List, Dict, Any
from datetime import datetime, timedelta
import dateutil.parser

import pybybit
from rich import print

import constants


# api_key='jPnEyte8ZeTBfWp9Db'
# api_secret='VBj5lBwyT8FtghqOwFN02Ia6bU1PBVU9EhU6'
coin = 'BTC'
symbol = coin + "USD"

api_key='3BKldShYBBQ7r7MfNP'  # testnet
api_secret='yv2E8EwGOIbGIZOKWREyEea0vnuXtVPq00k7'  # testnet

bybit = pybybit.API(key=api_key, secret=api_secret, testnet=True)


def order(qty, price=None, side='Buy', order_type='Limit'):
    res = bybit.rest.inverse.private_order_create(
        side=side,
        symbol=symbol,
        order_type=order_type,
        qty=qty,
        price=price,
        time_in_force='Good-Till-Canceled')
    return res.json()

def get_active_order():
    res = bybit.rest.inverse.private_order_list(
            symbol='BTCUSD',
            order_status="New")
    return res.json()

def cancel_all_active_orders() -> None:
    active_orders : List[Dict[str, Any]] = get_active_order()['result']['data']
    order_ids : List[str] = [active_order['order_id'] for active_order in active_orders]
    
    for order_id in order_ids:
        bybit.rest.inverse.private_order_cancel(
            symbol=symbol,
            order_id=order_id
        )


def get_kline():
    dt = datetime.now() - timedelta(hours=10)
    # dt = datetime.now() - timedelta(minutes=300)
    dt = int(dt.timestamp())
    res = bybit.rest.inverse.public_kline_list(
        symbol=symbol,
        interval=constants.DURATION_4H,
        from_=dt
    )
    result_info = res.json()['result']
    # timestamp = datetime.fromtimestamp(result_info['open_time'])
    return result_info


def get_position():
    res = bybit.rest.inverse.private_position_list(symbol=symbol)
    result_info = res.json()['result']
    return result_info


def set_leverage(leverage):
    res = bybit.rest.inverse.private_position_(symbol=symbol, leverage=leverage).json()


def get_wallet_balance():
    res = bybit.rest.inverse.private_wallet_balance()
    return res.json()



print(get_kline())

# while datetime.now().second >= 1:
#     time.sleep(0.5)

# print(datetime.now())


# bybit.ws.run_forever_inverse(topics=[
#     'orderBookL2_25.BTCUSD', 'trade.BTCUSD', 'insurance', 'instrument_info.100ms.BTCUSD', 'klineV2.1.BTCUSD',
#     'position', 'execution', 'order', 'stop_order',
# ])


# bybit.ws.run_forever_inverse(topics=[
#     'klineV2.1.BTCUSD',
# ])



# bybit.ws.add_callback(lambda msg, ws: print(msg))

# bybit.ws.run_forever_inverse(topics=[
#     'klineV2.1.BTCUSD',
# ])
# # bybit.ws.run_forever_inverse(topics=['trade.BTCUSD'])
# # 対話モード(REPL)でない場合スクリプトが終了する為、input関数で停止させる
# input()


