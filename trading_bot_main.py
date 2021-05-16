from concurrent.futures import ThreadPoolExecutor

from trading_brain.feature_creation import SingletonFeaturesCreator
from orders.orders import Trader
from logger import Logger

logger = Logger()
logger.remove_oldlog()


if __name__ == '__main__':

    features_creator = SingletonFeaturesCreator()
    trader = Trader()

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="thread") as executor:
            executor.submit(features_creator.create_features_in_realtime)
            executor.submit(trader.trade)