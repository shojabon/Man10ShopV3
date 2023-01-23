import datetime
import math
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class StorageRefillFunction(ShopFunction):
    allowed_shop_type = []

    # variables
    def on_function_init(self):
        self.set_variable("amount", 0)
        self.set_variable("minutes", 0)
        self.set_variable("last_refill_time", -1)
        self.set_variable("item_left", 0)

    def get_size(self):
        return self.get("size")

    def get_item_left(self):
        return self.get("item_left")

    def set_item_left(self, value: int):
        return self.set("item_left", value)

    def get_last_refill_time(self) -> int:
        return self.get("last_refill_time")

    def get_minutes(self):
        return self.get("minutes")

    def get_amount(self):
        return self.get("amount")

    # =========

    def calculate_last_refill_time(self):
        seconds_since_last_refill = datetime.datetime.now().timestamp() - self.get_last_refill_time()
        skipped_refills = seconds_since_last_refill / (self.get_minutes() * 60)
        return self.get_last_refill_time() + math.floor(skipped_refills) * self.get_minutes() * 60

    def transactions_left(self):
        if datetime.datetime.now().timestamp() - self.get_last_refill_time() >= self.get_minutes() * 60:
            self.set("last_refill_time", self.calculate_last_refill_time())
            self.set("item_left", self.get_amount())
        return self.get_item_left()

    def get_next_refill_time(self):
        if self.transactions_left() >= 1:
            return datetime.datetime.fromtimestamp(0)
        return datetime.datetime.fromtimestamp(self.get_last_refill_time() + self.get_minutes() * 60)

    # =========
    def is_function_enabled(self) -> bool:
        if self.get_minutes() == 0 or self.get_amount() == 0 or self.get_last_refill_time() == -1:
            return False
        return True

    def item_count(self, player: Player) -> Optional[int]:
        if self.shop.is_admin(): return -self.transactions_left()
        return self.transactions_left()

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.transactions_left() < order.amount:
            if self.shop.storage_function.get_item_count() == 0 and not self.shop.is_admin():
                order.player.warn_message("このショップは在庫不足です")
                return False
            if self.transactions_left() != 0:
                order.player.warn_message("現在" + str(self.transactions_left()) + "個まで取引することができます")
                return False
            if self.shop.get_shop_type() == "SELL":
                order.player.warn_message(
                    "このショップは買い取りを停止しています 次回の売却は " + self.get_next_refill_time().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                order.player.warn_message(
                    "このショップは品切れです 次回の入荷は " + self.get_next_refill_time().strftime("%Y-%m-%d %H:%M:%S"))
            return False
        return True

    def after_perform_action(self, order: OrderRequest):
        self.set_item_left(self.get_item_left() - order.amount)
