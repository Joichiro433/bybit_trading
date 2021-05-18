from typing import List, Dict, Union
import time

import constants
from trading_api.trading_api import ApiClient, Order, Position
from trading_brain.feature_creation import SingletonFeaturesCreator
from trading_brain.algorithms import Algorithms
from fund_management.fund_management import FundManager
from logger import Logger

logger = Logger()

class Trader:
    """リアルタイムトレードを行うクラス

    Attributes
    ----------
    api_client : ApiClient
        bybitAPIラッパーインスタンス
    features_creator : SingletonFeaturesCreator
        特徴量生成インスタンス
    algorithms : Algorithms
        注文を判断するインスタンス
    fund_manager : FundManager
        資産管理を行うインスタンス
    """
    def __init__(self) -> None:
        self.api_client = ApiClient()
        self.features_creator = SingletonFeaturesCreator()
        self.algorithms = Algorithms()
        self.fund_manager = FundManager()

    def trade(self):
        """リアルタイムトレードを行う"""
        while True:
            while not self.features_creator.has_updated:
                time.sleep(0.5)
            self.features_creator.has_updated = False
            signal, has_position  = self.algorithms.send_trading_signal()
            if signal is not None and has_position:
                # ポジションを決済
                self._settle_position()
            if signal is not None and not has_position:
                # ポジションを作成
                self._create_order(signal=signal)

    def _create_order(self, signal: str) -> None:
        """注文を出す

        Parameters
        ----------
        signal : str = constants.BUY | constans.SELL
            買い、もしくは売り
        """
        qty : int = self.fund_manager.cul_qty()
        order : Order = Order(
            side=signal,
            order_type=constants.MARKET,
            qty=qty,
            price=None)
        self.api_client.create_order(order=order)
        logger.info('order is created')
        logger.info(f'{order}')

    def _settle_position(self) -> None:
        """現在所有しているポジションを決済する"""
        now_position : Position = self.api_client.get_position()
        side : str = now_position.side
        size : int = now_position.size
        if side == constants.NONE:  # ポジションを所持していない時
            return None
        elif side == constants.BUY:
            side = constants.SELL
        elif side == constants.SELL:
            side = constants.BUY
        order : Order = Order(
            side=side,
            order_type=constants.MARKET,
            qty=size,
            price=None)
        self.api_client.create_order(order=order)  # ポジションの決済を行う
        logger.info('position is settled')
        logger.info(f'{order}')