import datetime
import traceback
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class DisabledFromFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("time", -1)

    def set_time(self, time: int):
        return self.set("time", time)

    def get_time(self) -> Optional[int]:
        return self.get("time")

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.get_time() != -1 and datetime.datetime.now().timestamp() >= self.get_time():
            order.player.warn_message("現在このショップは停止しています")
            return False
        return True