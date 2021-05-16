from typing import List, Dict, Union
import time

import constants
from trading_api.trading_api import ApiClient, Order
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

            signal : Union[str, None] = self.algorithms.send_trading_signal()
            if signal is not None:
                qty : float = self.fund_manager.cul_qty()

                order : Order = Order(
                    side=signal,
                    order_type=constants.MARKET,
                    qty=qty,
                    price=None)
                
                self.api_client.create_order(order=order)
                logger.info('order is created')
                logger.info(f'{order}')