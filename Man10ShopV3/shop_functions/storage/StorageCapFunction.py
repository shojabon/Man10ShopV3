from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class StorageCapFunction(ShopFunction):
    allowed_shop_type = []

    # variables
    def on_function_init(self):
        self.set_variable("size", 0)

    def get_size(self):
        return self.get("size")

    # =========

    def item_count(self, player: Player) -> Optional[int]:
        if self.shop.get_shop_type() == "SELL":
            return self.get_size()
        return super().item_count(player)

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            if self.shop.storage_function.get_item_count() + order.amount > self.get_size() != 0:
                order.player.warn_message("現在このショップは買い取りをしていません")
                return False
        return True

