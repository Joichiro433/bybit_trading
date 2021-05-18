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
    """Ohlcから特徴量を作成し、DataFrameに格納する役割をもつクラス、
    Singletonを継承しているため、プロパティはそれぞれのインスタンスで共有される

    Attributes
    ----------
    api_client : ApiClinet
        bybitAPIラッパーインスタンス
    terms : List[int]
        特徴量を生成に使用する期間のパターン
    has_updated : bool
        リアルタイムでohlcの情報を取得する際、更新が行われたか否かの情報
    df_features : pd.DataFrame
        指定の期間内のohlcと特徴量の情報を持つDataFrame

    Methods
    -------
    create_features_in_realtime -> None
        リアルタイムでdf_featuresの情報を更新する。
        更新間隔は、constants.UPDATE_INTERVALで指定
    """
    def __init__(self) -> None:
        self.api_client : ApiClient = ApiClient()
        self.terms : List[int] = [10, 50]
        self.has_updated : bool = False
        self._update_df_features()

    def create_features_in_realtime(self) -> None:
        """リアルタイムでdf_featuresの情報を更新する。
        更新間隔は、constants.UPDATE_INTERVALで指定
        """
        while True:
            self._update_df_features()
            self.has_updated = True
            logger.debug(f'{self.df_features}')
            time.sleep(constants.UPDATE_INTERVAL)

    def _update_df_features(self) -> None:
        """df_featuresの情報を更新する"""
        _ohlcs : List[Ohlc] = self.api_client.get_ohlcs()
        _df_ohlcs : pd.DataFrame = pd.DataFrame([ohlc.__dict__ for ohlc in _ohlcs])
        self.df_features : pd.DataFrame = self._create_features(df=_df_ohlcs)

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """ohlcの情報を用いて、特徴量を求める

        Parameters
        ----------
        df : pd.DataFrame
            ohlcの情報を持つDataFrame

        Returns
        -------
        pd.DataFrame
            ohlcと特徴量の情報を持つDataFrame
        """
        df = df.copy()
        df = self._cal_ATR(df=df, term=5)
        for term in self.terms:
            df = self._cal_SMA(df=df, term=term)
            df = self._cal_std(df=df, term=term)
            df = self._cal_EMA(df=df, term=term)
        df = self._cal_MACD(df=df, short_term=9, long_term=17, signal_term=7)
        df = self._cal_max_min_price(df=df, term=20)
        return df.dropna()

    def _cal_ATR(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        """ATR(Average True Range)を求める

        Parameters
        ----------
        df : pd.DataFrame
            ohlcの情報を持つDataFrame
        term : int
            計算する期間

        Returns
        -------
        pd.DataFrame
            ohlcとATRの情報を持つDataFrame
        """
        df = df.copy()
        df[f'ATR_{term}'] = (df['high'].rolling(window=term).sum() - df['low'].rolling(window=term).sum()) / term
        return df

    def _cal_SMA(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        """SMA(Simple Moving Average)を求める

        Parameters
        ----------
        df : pd.DataFrame
            ohlcの情報を持つDataFrame
        term : int
            計算する期間

        Returns
        -------
        pd.DataFrame
            ohlcとSMAの情報を持つDataFrame
        """
        df = df.copy()
        df[f'sma_{term}'] = df['close'].rolling(window=term).mean()
        return df

    def _cal_std(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        """ある期間の標準偏差を求める

        Parameters
        ----------
        df : pd.DataFrame
            ohlcの情報を持つDataFrame
        term : int
            計算する期間

        Returns
        -------
        pd.DataFrame
            ohlcとstdの情報を持つDataFrame
        """
        df = df.copy()
        df[f'std_{term}'] = df['close'].rolling(window=term).std()
        return df

    def _cal_EMA(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        """EMA(Exponential Moving Average)を求める

        Parameters
        ----------
        df : pd.DataFrame
            ohlcの情報を持つDataFrame
        term : int
            計算する期間

        Returns
        -------
        pd.DataFrame
            ohlcとEMAの情報を持つDataFrame
        """
        df = df.copy()
        df[f'ema_{term}'] = df['close'].ewm(span=term, adjust=False).mean()
        return df

    def _cal_MACD(self, df: pd.DataFrame, short_term: int, long_term: int, signal_term: int) -> pd.DataFrame:
        """MACDを求める

        Parameters
        ----------
        df : pd.DataFrame
            ohlcの情報を持つDataFrame
        short_term : int
            macdの短期期間
        long_term : int
            macdの長期期間
        signal_term : int
            シグナルの期間

        Returns
        -------
        pd.DataFrame
            ohlcとMACD, シグナルの情報を持つDataFrame
        """
        df = df.copy()
        ema_short = df['close'].ewm(span=short_term, adjust=False).mean()
        ema_long= df['close'].ewm(span=long_term, adjust=False).mean()
        df[f'macd'] = (ema_short - ema_long)
        df[f'macd_signal'] = (ema_short - ema_long).ewm(span=signal_term, adjust=False).mean()
        return df

    def _cal_max_min_price(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        """指定の期間の最高値、最安値を求める

        Parameters
        ----------
        df : pd.DataFrame
            ohlcの情報を持つDataFrame
        term : int
            計算する期間

        Returns
        -------
        pd.DataFrame
            ohlcと指定の期間の最高値、最安値の情報を持つDataFrame
        """
        df = df.copy()
        df[f'max_price'] = df['high'].rolling(window=term).max()
        df[f'min_price'] = df['low'].rolling(window=term).min()
        return df
