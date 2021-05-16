import constants

import numpy as np

from trading_brain.feature_creation import SingletonFeaturesCreator
from logger import Logger

logger = Logger()

class Algorithms:
    """特徴量を吟味して、注文を出すか否かを判断する

    Todo
    ----
    吟味する指標を増やして、重みつきアンサンブルをとるように改修
    """
    def __init__(self) -> None:
        self.features_creator = SingletonFeaturesCreator()
        self.signal_flag : int = 0
        
    def send_trading_signal(self):
        self.signal_flag = 0
        self._judge_by_MACD()
        if self.signal_flag >= 1:
            return constants.BUY
        if self.signal_flag <= -1:
            return constants.SELL
        return None

    def _judge_by_MACD(self):
        macd = np.array(self.features_creator.df_features['macd'])
        macd_signal = np.array(self.features_creator.df_features['macd_signal'])

        before_macd, after_macd = macd[-2], macd[-1]
        before_signal, after_signal = macd_signal[-2], macd_signal[-1]

        # 買いのシグナル
        if before_macd < 0 and before_signal < 0:
            if before_macd < before_signal and after_macd > after_signal:
                self.signal_flag = 1
                logger.info('MACD made a buying decision')

        # 売りのシグナル
        if before_macd > 0 and before_signal > 0:
            if before_macd > before_signal and after_macd < after_signal:
                self.signal_flag = -1
                logger.info('MACD made a selling decision')