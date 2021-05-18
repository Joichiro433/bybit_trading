import numpy as np

import constants
from trading_brain.feature_creation import SingletonFeaturesCreator
from logger import Logger

logger = Logger()


class Judgement:
    def __init__(self, position_side : str) -> None:
        self.signal_to_create_order : int = 0
        _featuers_creator = SingletonFeaturesCreator()
        self.df_features = _featuers_creator.df_features
        self.position_side : str = position_side
        self._judge_by_ensemble()

    def _judge_by_ensemble(self):
        self._judge_by_donchian()
        # self._judge_by_MACD()

    def _judge_by_donchian(self):
        now_price : float = self.df_features.iloc[-1]['close']
        max_price_over_past : float = self.df_features.iloc[-2]['max_price']
        min_price_over_past : float = self.df_features.iloc[-2]['min_price']
        if (now_price > max_price_over_past) and (not self.position_side == constants.BUY):
            self.signal_to_create_order += 1
            logger.info('donchian made a buying decision')
        if (now_price < min_price_over_past) and (not self.position_side == constants.SELL):
            self.signal_to_create_order -= 1
            logger.info('donchian made a selling decision')

    def _judge_by_MACD(self):
        macd = np.array(self.features_creator.df_features['macd'])
        macd_signal = np.array(self.features_creator.df_features['macd_signal'])

        before_macd, after_macd = macd[-2], macd[-1]
        before_signal, after_signal = macd_signal[-2], macd_signal[-1]

        if self.position_side == constants.NONE:
            # ポジションを保持していない時
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

        elif self.position_side == constants.BUY:
            # 買いのポジションを保持している時
            if before_macd > 0 and before_signal > 0:
                if before_macd > before_signal and after_macd < after_signal:
                    self.signal_flag = -1
                    logger.info('MACD made a selling decision')

        elif self.position_side == constants.SELL:
            # 売りのポジションを保持している時
            if before_macd < 0 and before_signal < 0:
                if before_macd < before_signal and after_macd > after_signal:
                    self.signal_flag = 1
                    logger.info('MACD made a buying decision')
