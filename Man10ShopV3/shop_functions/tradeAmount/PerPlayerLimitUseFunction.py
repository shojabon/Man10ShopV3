import datetime
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class PerPlayerLimitUseFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        pass

    def get_permission_user_limits(self):
        limits = {}
        for permission_player in self.shop.permission_function.get_users():
            player = Player()
            player.uuid = permission_player["uuid"]
            player.main = self.shop.api.main
            limits[player.get_uuid_formatted()] = self.get_count(player)
        return limits
    def set_count(self, player: Player, count: int):
        result = player.set_data(self, "count", count)
        return result

    def get_count(self, player: Player) -> Optional[int]:
        return player.get_data(self, "count")

    def item_count(self, player: Player) -> Optional[int]:
        self.set_dynamic_variable("user_count", self.get_permission_user_limits())
        if player is not None and self.get_count(player) is not None:
            if self.shop.is_admin(): return -self.get_count(player)
            return self.get_count(player)
        return super().item_count(player)

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.get_count(order.player) is not None:
            if self.get_count(order.player) == 0:
                order.player.warn_message("ショップの使用回数制限に達しました")
                return False
        return True

    def after_perform_action(self, order: OrderRequest):
        if self.get_count(order.player) is not None:
            self.set_count(order.player, self.get_count(order.player) - 1)



