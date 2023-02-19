import datetime
import time
import traceback
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class PerMinuteCoolDownFunction(ShopFunction):
    allowed_shop_type = []

    time_cache = {}
    # uuid : amount, first_trade_time,

    def on_function_init(self):
        self.set_variable("time", 0)
        self.set_variable("amount", 0)

    def set_time(self, time: int):
        return self.set("time", time)

    def get_time(self) -> int:
        return self.get("time")

    def set_amount(self, amount: int):
        return self.set("amount", amount)

    def get_amount(self) -> int:
        return self.get("amount")

    # =====

    def player_in_time_trade_count(self, player: Player):
        try:
            trade_log = player.get_data(self, "trade_log", [])
            bought_count = 0
            new_log = []
            current_time = datetime.datetime.now().timestamp()
            time_range = self.get_time() * 60
            for log in trade_log:
                if log["time"].timestamp() < current_time - time_range:
                    continue
                bought_count += log["amount"]
                new_log.append(log)
            player.set_data(self, "trade_log", new_log)
            return bought_count
        except Exception:
            traceback.print_exc()
            return None

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        player_trade_count_in_time = self.player_in_time_trade_count(order.player)

        if player_trade_count_in_time is None:
            order.player.warn_message("内部エラーが発生しました")
            return False

        if player_trade_count_in_time + order.amount > self.get_amount():
            order.player.warn_message("時間内の最大取引数に達しています")
            return False

        return True

    def after_perform_action(self, order: OrderRequest):
        trade_log = order.player.get_data(self, "trade_log", [])
        trade_log.append({"time": datetime.datetime.now(), "amount": order.amount})
        order.player.set_data(self, "trade_log", trade_log)

    def item_count(self, player: Player) -> Optional[int]:
        if player is None:
            return 0

        count = self.get_amount() - self.player_in_time_trade_count(player)
        if self.shop.is_admin():
            return -count
        if count < 0:
            return 0
        return count

    def is_function_enabled(self) -> bool:
        if self.get_time() == 0 or self.get_amount() == 0:
            return False
        return True
