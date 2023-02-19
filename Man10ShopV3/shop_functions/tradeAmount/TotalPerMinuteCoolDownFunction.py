import datetime
import traceback
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class TotalPerMinuteCoolDownFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("time", 0)
        self.set_variable("amount", 0)

        self.set_variable("trade_log", [], visible_in_json=False)

    def set_time(self, time: int):
        return self.set("time", time)

    def get_time(self) -> int:
        return self.get("time")

    def set_amount(self, amount: int):
        return self.set("amount", amount)

    def get_amount(self) -> int:
        return self.get("amount")

    def get_trade_log(self):
        return self.get("trade_log")

    def set_trade_log(self, log):
        return self.set("trade_log", log)

    # =====

    def in_time_trade_count(self):
        try:
            trade_log = self.get_trade_log()
            bought_count = 0
            new_log = []
            for log in trade_log:
                if log["time"].timestamp() < datetime.datetime.now().timestamp() - self.get_time() * 60:
                    continue
                bought_count += log["amount"]
                new_log.append(log)

            return bought_count
        except Exception:
            traceback.print_exc()
            return None

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        player_trade_count_in_time = self.in_time_trade_count()
        if player_trade_count_in_time is None:
            order.player.warn_message("内部エラーが発生しました")
            return False
        if player_trade_count_in_time + order.amount > self.get_amount():
            order.player.warn_message("時間内の最大取引数に達しています")
            return False
        return True

    def after_perform_action(self, order: OrderRequest):
        trade_log = self.get_trade_log()
        trade_log.append({"time": datetime.datetime.now(), "amount": order.amount})
        self.set_trade_log(trade_log)

    def item_count(self, player: Player) -> Optional[int]:
        if player is None:
            return 0
        count = self.get_amount() - self.in_time_trade_count()
        if self.shop.is_admin():
            return -count
        if count < 0:
            return 0
        return count

    def is_function_enabled(self) -> bool:
        return self.get_time() != 0 and self.get_amount() != 0

