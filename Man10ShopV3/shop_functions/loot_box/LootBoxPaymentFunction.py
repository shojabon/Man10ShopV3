from typing import Optional

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class LootBoxPaymentFunction(ShopFunction):
    allowed_shop_type = ["LOOT_BOX"]

    # variables
    def on_function_init(self):
        self.set_variable("cash", 0)
        self.set_variable("item", None)

    def get_cash(self):
        return self.get("cash")

    def get_item(self) -> Optional[ItemStack]:
        if self.get("item") is None:
            return None
        return ItemStack().from_json(self.get("item"))

    # =========

    def is_function_enabled(self) -> bool:
        return self.get_cash() == 0 and self.get_item() is None

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.get_cash() != 0:
            if not order.player.get_balance() < self.get_cash():
                order.player.warn_message("現金が足りません")
                return False
        if self.get_item() is not None:
            if not order.player.item_check(self.get_item().type_base64, self.get_item().amount):
                order.player.warn_message("アイテムが足りません")
                return False
        return True

    def perform_action(self, order: OrderRequest) -> bool:
        if self.get_cash() != 0:
            if not order.player.take_money(self.get_cash()):
                order.player.warn_message("現金が足りません")
                return False
        if self.get_item() is not None:
            if not order.player.item_take(self.get_item().type_base64, self.get_item().amount):
                order.player.warn_message("アイテムが足りません")
                return False
        return True

