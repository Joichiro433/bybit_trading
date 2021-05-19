from typing import List, Dict, Union

import math

import constants
from trading_api.trading_api import ApiClient, Position
from trading_brain.feature_creation import SingletonFeaturesCreator

class FundManager:
    def __init__(self) -> None:
        self.api_client : ApiClient = ApiClient()
        _features_creator = SingletonFeaturesCreator()
        _df_features = _features_creator.df_features
        self.now_price : float = _df_features.iloc[-1]['close']
        self.ATR : float = _df_features.iloc[-1]['close']

    def decide_if_stop_position(self) -> bool:
        now_position : Position = self.api_client.get_position()
        side_sign : int = 1 if now_position.side==constants.BUY else -1  #ポジションが買いの時:1, 売りの時:-1 

        entry_price : float = now_position.entry_price
        stop_price : float = self.now_price - side_sign * self.ATR * constants.STOP_RANGE
        
        if entry_price < stop_price * side_sign:
            return True
        return False

    def cul_qty(self) -> int:
        available_USD : float = self.api_client.get_available_balance() * self.now_price
        range_for_stop_loss : float = self.ATR * constants.STOP_RANGE / self.now_price

        qty : int = math.floor(available_USD * constants.ACCEPTSBEL_LOSS_RATE / range_for_stop_loss)

        return qty