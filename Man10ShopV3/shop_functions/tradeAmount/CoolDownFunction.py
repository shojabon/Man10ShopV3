import datetime
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class CoolDownFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("seconds", 0)

    def set_seconds(self, name: int):
        return self.set("seconds", name)

    def get_seconds(self) -> int:
        return self.get("seconds")

    # =================

    def set_cooldown_time(self, player: Player):
        player.set_data(self.shop.get_shop_id(), "cooldown.last_bought", datetime.datetime.now())

    def get_cooldown_time(self, player: Player):
        return player.get_data(self.shop.get_shop_id(), "cooldown.last_bought")

    def check_cooldown(self, player: Player):
        cooldown_time = self.get_seconds()
        if cooldown_time == 0: return False
        current_time = datetime.datetime.now().timestamp()
        if current_time is None: return True
        return current_time - self.get_cooldown_time(player).timestamp() < cooldown_time

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.check_cooldown(order.player):
            order.player.send_message(str(self.get_seconds()) + "秒のクールダウン中です")
            return False

    def after_perform_action(self, order: OrderRequest):
        self.set_cooldown_time(order.player)
