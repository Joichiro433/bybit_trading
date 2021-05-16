from datetime import datetime
import time

from concurrent.futures import ThreadPoolExecutor

from rich import print

from logger import Logger
from trading_api.trading_api import ApiClient, Order
from trading_brain.feature_creation import SingletonFeaturesCreator
from orders.orders import Trader

logger = Logger()
logger.remove_oldlog()


if __name__ == '__main__':

    features_creator = SingletonFeaturesCreator()
    # print(features_creator.df_features)
    # trader = Trader()

    # with ThreadPoolExecutor(max_workers=2, thread_name_prefix="thread") as executor:
    #         executor.submit(features_creator.create_features_in_realtime)
    #         executor.submit(trader.trade)

    api_client = ApiClient()

    # order : Order = Order(
    #                 side='Buy',
    #                 order_type='Market',
    #                 qty=10,
    #                 price=None)

    # print(api_client.create_order(order=order))

    


    # print(features_creater.df_features)
    # print(datetime.now())

    # for ohlc in api_client.get_realtime_ohlc():
    #     print(ohlc)
    #     print(datetime.now())



    def print_df():
        while True:
            while not features_creator.has_updated:
                time.sleep(0.5)
            features_creator.has_updated = False
            print(features_creator.df_features)
            print(datetime.now())
            time.sleep(20)


    
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="thread") as executor:
            executor.submit(features_creator.create_features_in_realtime)
            executor.submit(print_df)
