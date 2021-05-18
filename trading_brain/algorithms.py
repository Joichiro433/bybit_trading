import constants

import numpy as np

import constants
from trading_api.trading_api import ApiClient
from trading_brain.feature_creation import SingletonFeaturesCreator
from trading_brain.judgement import Judgement
from logger import Logger

logger = Logger()


class Algorithms:
    """特徴量を吟味して、注文を出すか否かを判断する

    Todo
    ----
    吟味する指標を増やして、重みつきアンサンブルをとるように改修
    """
    def __init__(self) -> None:
        self.api_client = ApiClient()
        self.position_side : str
        
    def send_trading_signal(self):
        # シグナルの初期化
        has_position : bool = self._check_if_has_position()
        judgement = Judgement(position_side=self.position_side)  # judgementインスタンスの初期化
        
        if judgement.signal_to_create_order >= 1:
            return constants.BUY, has_position
        if judgement.signal_to_create_order <= -1:
            return constants.SELL, has_position
        return None, has_position

    def _check_if_has_position(self) -> bool:
        self.position_side : str = self.api_client.get_position().side
        has_position : bool = False if self.position_side == constants.NONE else True
        return has_position