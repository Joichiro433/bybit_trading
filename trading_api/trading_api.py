import time
from datetime import datetime, timedelta
import dateutil.parser
import requests
from typing import Any, Dict, List, Union, Iterator, Tuple

import pybybit

from logger import Logger
import constants
import settings


logger = Logger()
symbol = settings.symbol
coin = symbol[:3]

unit_time_to_get_a_ohlc = constants.DURATION_1M
number_of_ohlcs_to_get = constants.NUMBER_OF_OHLCS


class Ohlc:
    """ローソク足の情報をもつクラス

    Attributes
    ----------
    open_time : datetime
        ローソク足の取得時刻
    open : float
        始値
    high : float
        高値
    low : float
        安値
    close : float
        終値
    """
    def __init__(
            self, 
            open_time: datetime, 
            open: float, 
            high: float, 
            low: float, 
            close: float) -> None:
        self.open_time : datetime = open_time
        self.open : float = open
        self.high : float = high
        self.low : float = low
        self.close : float = close

    def __str__(self) -> str:
        return str(self.__dict__)


class Order:
    """注文の情報をもつクラス

    Attributes
    ----------
    side : str = constants.BUY | constants.SELL
        買い、もしくは売り
    order_type : str = constans.LIMIT | constans.MARKET | constans.STOP
        成行、指値、逆指値
    qty : float
        ポジションサイズ
    price : float | None
        注文の値段。成行注文の場合はNoneとする
    created_at : datetime | None
        注文が作成された時刻。注文を出す際はNoneと指定
    updated_at : datetime | None
        注文が更新された時刻。注文を出す際はNoneと指定
    """
    def __init__(
            self, 
            side: str, 
            order_type: str, 
            qty: int, 
            price: Union[float, None], 
            created_at: Union[datetime, None] = None,
            updated_at: Union[datetime, None] = None) -> None:
        self.side : str = side
        self.order_type : str = order_type
        self.qty : int = qty
        self.price : Union[float, None] = price
        self.created_at : Union[datetime, None] = created_at
        self.updated_at : Union[datetime, None] = updated_at

    def __str__(self) -> str:
        return str(self.__dict__)


class Position:
    """ポジションの情報をもつクラス

    Attributes
    ----------
    side : str = constants.BUY | constants.SELL
        買い、もしくは売り
    size : int
        ポジションサイズ
    entry_price : float
        ポジションをもった時点の値段
    leverage : float
        レバレッジの値
    liq_price : float
        強制ロスカットの値段
    created_at : datetime
        ポジションを持った際の時刻
    updated_at : datetime
        ポジションを更新した際の時刻
    """
    def __init__(
            self,
            side: str,
            size: float,
            entry_price: float,
            leverage: float,
            liq_price: float,
            created_at: datetime,
            updated_at: datetime) -> None:
        self.side : str = side
        self.size : float = size
        self.entry_price : float = entry_price
        self.leverage : float = leverage
        self.liq_price : float = liq_price
        self.created_at : datetime = created_at
        self.updated_at : datetime = updated_at
    
    def __str__(self) -> str:
        return str(self.__dict__)


class ApiClient:
    """bybitのAPIを使用するクラス

    Attributes
    ----------
    client : pybybit.API
        pybybitライブラリを用いたAPIラッパーインスタンス。
        settings.iniでtestnet環境か本番環境かを指定する
    
    Methods
    -------
    get_available_balance -> flaot
        現在の残高（Bitcoinの残高など）を取得する
    get_ohlcs -> List[Ohlc]
        現在時刻から指定の分数間のローソク足情報を取得する
    get_realtime_ohlc -> Iterator[Ohlc]
        ローソク足の情報が更新される度にその情報を取得する
    get_position -> Position
        現在のポジション情報を取得する
    get_active_orders -> List[Order | None]
        現在確約していない全ての注文のリストで返却する。存在しなければ空リストを返却する
    create_order -> None
        注文を出す
    cancel_all_active_orders -> None:
        現在確約していない全ての注文をキャンセルする
    """
    def __init__(self) -> None:
        if settings.is_testnet:
            self.client : pybybit.API = pybybit.API(
                key=settings.testnet_api_key, 
                secret=settings.tesetnet_api_secret_key,
                testnet=True)
        else:
            self.client : pybybit.API = pybybit.API(
                key=settings.api_key, 
                secret=settings.api_secret_key)

    def get_available_balance(self) -> float:
        """現在の残高（Bitcoinの残高など）を取得する

        Returns
        -------
        float
            現在の残高（Bitcoinの残高など）
        """
        resp : requests.Response = self.client.rest.inverse.private_wallet_balance(coin=coin)
        wallet_balance : float = resp.json()["result"][f"{coin}"]["available_balance"]
        return wallet_balance

    def get_ohlcs(
            self,
            time_interval: str = unit_time_to_get_a_ohlc, 
            num_ohlcs: int = number_of_ohlcs_to_get) -> List[Ohlc]:
        """現在時刻から指定の分数間のローソク足情報を取得する

        Parameters
        ----------
        time_interval : str = constants.DURATION_1M | constants.DURATION_5M | ...
            ローソク足を取得する単位時間

        num_ohlcs : int
            取得するohlcの個数
            e.g.) num_ohlcs=200 の時は現在時刻から200単位時間の間のローソク足情報を取得する

        Returns
        -------
        List[Ohlc]
            現在時刻から指定の単位時間間のローソク足情報
        """
        def __cal_start_time(time_interval: int, num_ohlcs: int) -> Tuple[int, int]:
            if time_interval == constants.DURATION_1M:
                delta, unit_time = timedelta(minutes=num_ohlcs), 1
            elif time_interval == constants.DURATION_5M:
                delta, unit_time = timedelta(minutes=num_ohlcs*5), 5
            elif time_interval == constants.DURATION_30M:
                delta, unit_time = timedelta(minutes=num_ohlcs*30), 30
            elif time_interval == constants.DURATION_1H:
                delta, unit_time = timedelta(hours=num_ohlcs), 60
            elif time_interval == constants.DURATION_4H:
                delta, unit_time = timedelta(hours=num_ohlcs*4), 60*4
            elif time_interval == constants.DURATION_1DAY:
                delta, unit_time = timedelta(days=num_ohlcs), 60*24
            return int((datetime.now() - delta).timestamp()), unit_time

        ohlcs : List[Ohlc] = []
        now : int = int(datetime.now().timestamp())  # 現在時刻のタイムスタンプ
        start_time, unit_time = __cal_start_time(time_interval, num_ohlcs)  # ohlcの取得開始時刻のタイムスタンプ, ohlcを取得する単位時間
        while start_time < now:
            resp : requests.Response = self.client.rest.inverse.public_kline_list(
                symbol=symbol,
                interval=time_interval,
                from_=start_time)
            ohlc_info : List[Dict[str, Union[str, int]]] = resp.json()['result']
            ohlcs += [self._parse_ohlc_from_dict(dict) for dict in ohlc_info]
            start_time += 200 * 60 * unit_time  # 200単位時間すすめる

        return ohlcs

    def _parse_ohlc_from_dict(self, dict) -> Ohlc:
        """dictとして返却されるローソク足情報を、Ohlcインスタンスに変換する

        Parameters
        ----------
        dict : Dict[str, Union[str, int]]
            bybitAPIによって返却されるローソク足情報

        Returns
        -------
        Ohlc
            Ohlcインスタンスに変換されたローソク足情報
        """
        ohlc : Ohlc = Ohlc(
            open_time=datetime.fromtimestamp(dict['open_time']),
            open=float(dict['open']),
            high=float(dict['high']),
            low=float(dict['low']),
            close=float(dict['close']))
        return ohlc
    
    def get_position(self) -> Position:
        """現在のポジション情報を取得する。ポジションを持っていなければNoneを返却する

        Returns
        -------
        Position
            現在のポジション情報
        """
        resp : requests.Response = self.client.rest.inverse.private_position_list(symbol=symbol)
        position_info : Dict[str: Union[str, float]] = resp.json()['result']
        position : Position = Position(
            side=position_info['side'],
            size=float(position_info['size']),
            entry_price=float(position_info['entry_price']),
            leverage=float(position_info['leverage']),
            liq_price=float(position_info['liq_price']),
            created_at=dateutil.parser.parse(position_info['created_at']),
            updated_at=dateutil.parser.parse(position_info['updated_at']))
        return position
        
    def get_active_orders(self) -> List[Union[Order, None]]:
        """現在確約していない全ての注文のリストで返却する。存在しなければ空リストを返却する

        Returns
        -------
        List[Union[Order, None]]
            現在確約していない全ての注文のリスト。存在しなければ空リスト
        """
        def __parse_order_from_dict(dict : Dict[str, Union[str, float]]) -> Order:
            order : Order = Order(
                side=dict['side'],
                order_type=dict['order_type'],
                qty=int(dict['qty']),
                price=float(dict['price']),
                created_at=dateutil.parser.parse(dict['created_at']),
                updated_at=dateutil.parser.parse(dict['updated_at']))
            return order
            
        resp : requests.Response = self.client.rest.inverse.private_order_list(
            symbol=symbol,
            order_status='New')
        active_orders_info : List[Union[Dict[str, Union[str, float]]], None] = resp.json()['result']['data']
        Orders : List[Union[Order, None]] = [__parse_order_from_dict(dict) for dict in active_orders_info]
        return Orders

    def create_order(self, order: Order) -> None:
        """注文を出す

        Parameters
        ----------
        order : Order
            出す注文の情報
        """
        resp = self.client.rest.inverse.private_order_create(
            symbol=symbol,
            qty=order.qty,
            side=order.side,
            order_type=order.order_type,
            price=order.price,
            time_in_force='Good-Till-Canceled')
        return resp

    def cancel_all_active_orders(self) -> None:
        """現在確約していない全ての注文をキャンセルする"""
        self.client.rest.inverse.private_order_cancelall(symbol=symbol)