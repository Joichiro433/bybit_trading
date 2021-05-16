from typing import List, Any

import pandas as pd
import plotly.graph_objects as go

from trading_brain.feature_creation import SingletonFeaturesCreator

class Plotter:
    def __init__(self) -> None:
        _feature_creator : SingletonFeaturesCreator = SingletonFeaturesCreator()
        self.df_features : pd.DataFrame = _feature_creator.df_features
        self.ploted_data : List[Any] = []

    def plot_chart(self):
        self._add_ohlc_to_ploted_data()
        self._add_sma_to_ploted_data()
        fig = go.Figure(data=self.ploted_data)
        fig.write_html("test.html")
        fig.show()

    def _add_ohlc_to_ploted_data(self):
        ohlc_data = go.Candlestick(
            x=self.df_features['open_time'],
            open=self.df_features['open'],
            high=self.df_features['high'],
            low=self.df_features['low'],
            close=self.df_features['close'],
            name='ohlc')
        self.ploted_data.append(ohlc_data)

    def _add_sma_to_ploted_data(self):
        sma_data = go.Scatter(
            x=self.df_features['open_time'],
            y=self.df_features['ema_10'],
            name='ema_10',
            opacity=0.6,  # 透明度
            marker={'color':'#ffd12a'})
        self.ploted_data.append(sma_data)


if __name__ == '__main__':
    plotter = Plotter()

    plotter.plot_chart()