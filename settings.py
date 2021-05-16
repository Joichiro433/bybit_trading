import configparser

from utils.utils import bool_from_str

conf = configparser.ConfigParser()
conf.read('settings.ini')

is_testnet = bool_from_str(conf['bybit']['is_testnet'])

api_key = conf['bybit']['api_key']
api_secret_key = conf['bybit']['api_secret_key']
testnet_api_key = conf['bybit']['testnet_api_key']
tesetnet_api_secret_key = conf['bybit']['tesetnet_api_secret_key']

symbol = conf['bybit']['symbol']