from typing import List, Dict, Union
import time

import pandas as pd

import constants
from trading_api.trading_api import ApiClient, Ohlc
from logger import Logger

logger = Logger()

class Singleton:
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class SingletonFeaturesCreator(Singleton):
    def __init__(self) -> None:
        self.api_client : ApiClient = ApiClient()
        self.terms : List[int] = [10, 50]
        self.max_term : int = max(self.terms)
        self.has_updated = False
        self._update_df_features()

    def _update_df_features(self) -> None:
        _ohlcs : List[Ohlc] = self.api_client.get_ohlcs()
        _df_ohlcs : pd.DataFrame = pd.DataFrame([ohlc.__dict__ for ohlc in _ohlcs])
        self.df_features = self._create_features(df=_df_ohlcs)

    def create_features_in_realtime(self) -> None:
        while True:
            self._update_df_features()
            self.has_updated = True
            time.sleep(constants.UPDATE_INTERVAL)

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = self._cal_ATR(df=df, term=5)
        for term in self.terms:
            df = self._cal_SMA(df=df, term=term)
            df = self._cal_std(df=df, term=term)
            df = self._cal_EMA(df=df, term=term)
        df = self._cal_MACD(df=df, short_term=9, long_term=17, signal_term=7)
        return df.dropna()

    def _cal_ATR(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        df = df.copy()
        df[f'ATR_{term}'] = (df['high'].rolling(window=term).sum() - df['low'].rolling(window=term).sum()) / term
        return df

    def _cal_SMA(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        df = df.copy()
        df[f'sma_{term}'] = df['close'].rolling(window=term).mean()
        return df

    def _cal_std(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        df = df.copy()
        df[f'std_{term}'] = df['close'].rolling(window=term).std()
        return df

    def _cal_EMA(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        df = df.copy()
        df[f'ema_{term}'] = df['close'].ewm(span=term).mean()
        return df

    def _cal_MACD(self, df: pd.DataFrame, short_term: int, long_term: int, signal_term: int) -> pd.DataFrame:
        df = df.copy()
        ema_short = df['close'].ewm(span=short_term, adjust=False).mean()
        ema_long= df['close'].ewm(span=long_term, adjust=False).mean()
        df[f'macd'] = (ema_short - ema_long)
        df[f'macd_signal'] = (ema_short - ema_long).ewm(span=signal_term, adjust=False).mean()
        return df