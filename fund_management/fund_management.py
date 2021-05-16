from typing import List, Dict, Union

from trading_api.trading_api import ApiClient, Position

class FundManager:
    def __init__(self) -> None:
        self.api_client : ApiClient = ApiClient()

    def cut_loss():
        pass

    def cul_qty(self) -> int:
        now_size : float = self.api_client.get_position().size
        if now_size == 0.0:
            return 10
        return int(now_size * 2)