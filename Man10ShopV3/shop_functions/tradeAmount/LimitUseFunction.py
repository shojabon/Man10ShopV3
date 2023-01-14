import datetime
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class LimitUseFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("count", None)

    def set_count(self, name: Optional[int]):
        return self.set("count", name)

    def get_count(self) -> Optional[int]:
        return self.get("count")

    def item_count(self, player: Player) -> Optional[int]:
        if self.get_count() is not None:
            if self.shop.is_admin(): return -self.get_count()
            return self.get_count()
        return super().item_count(player)

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.get_count() is not None:
            if self.get_count() == 0:
                order.player.warn_message("ショップの使用回数制限に達しました")
                return False
        return True

    def after_perform_action(self, order: OrderRequest):
        if self.get_count() is not None:
            self.set_count(self.get_count() - 1)
