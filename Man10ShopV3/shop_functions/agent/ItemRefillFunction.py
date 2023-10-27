import datetime
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class ItemRefillFunction(ShopFunction):
    allowed_shop_type = []

    # variables
    def on_function_init(self):
        self.set_variable("amount", 0)
        self.set_variable("time", 0)
        self.set_variable("last_refill_time", -1)

    def get_size(self):
        return self.get("size")

    def get_last_refill_time(self) -> int:
        return self.get("last_refill_time")

    def get_time(self):
        return self.get("time")

    def get_amount(self):
        return self.get("amount")

    # =========

    def calculate_last_refill_time(self):
        seconds_since_last_refill = datetime.datetime.now().timestamp() - self.get_last_refill_time()
        skipped_refills = seconds_since_last_refill / (self.get_time() * 60)
        return self.get_last_refill_time() + skipped_refills * self.get_time() * 60

    def calculate_item_to_refill(self):
        if datetime.datetime.now().timestamp() - self.get_last_refill_time() >= self.get_time() * 60:
            self.set("last_refill_time", self.calculate_last_refill_time())
            self.shop.storage_function.set_item_count(self.get_amount())

    # =========
    def is_function_enabled(self) -> bool:
        if self.get_time() == 0 or self.get_amount() == 0 or self.get_last_refill_time() == -1:
            return False
        return True

    def per_minute_execution_task(self):
        self.calculate_item_to_refill()