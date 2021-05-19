from datetime import datetime

DURATION_1M = '1'
# DURATION_3M = '3'
DURATION_5M = '5'
# DURATION_15M = '15'
DURATION_30M = '30'
DURATION_1H = '60'
# DURATION_2H = '120'
DURATION_4H = '240'
# DURATION_6H = '360'
# DURATION_12H = '720'
DURATION_1DAY = 'D'
# DURATION_1WEEK = 'W'
# DURATION_1MANTH = 'M'

BUY = 'Buy'
SELL = 'Sell'
NONE = 'None'

LIMIT = 'Limit'
MARKET = 'Market'
STOP = 'Stop'

NUMBER_OF_OHLCS = 1000
UPDATE_INTERVAL = 20

STOP_RANGE = 2.0  # 損切りを行う閾値幅の倍率
ACCEPTSBEL_LOSS_RATE = 0.001  # 全資産のうち、損失を許容する割合

timestamp = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
db_name = f'bybit_pl_{timestamp}.sql'