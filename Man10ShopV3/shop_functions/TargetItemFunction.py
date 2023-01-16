import codecs
import hashlib

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class TargetItemFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    # variables

    def on_function_init(self):
        self.set_variable("item", ItemStack().base64, variable_check=self.on_set_target_item)
        self.set_variable("item_hash", ItemStack().md5)

    def get_target_item(self) -> str:
        return self.get("item")

    def set_target_item(self, item_base64: str):
        return self.set("item", item_base64)

    def get_target_item_hash(self):
        return self.get("item_hash")

    def set_target_item_hash(self, item_hash: str):
        return self.set("item_hash", item_hash)

    # =========

    def on_set_target_item(self, player: Player, new_value):
        if not self.shop.is_admin() and self.shop.storage_function.get_item_count() != 0:
            player.warn_message("アイテム変更時は在庫が空なくてはいけません")
            return False
        return True

    def perform_action(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "BUY":
            if not self.shop.storage_function.remove_item_count(order.amount):
                order.player.warn_message("内部エラーが発生しました")
                return False
            order.player.item_give(self.get_target_item(), order.amount)  # check for exceptions ?
        if self.shop.get_shop_type() == "SELL":
            item_take_request = order.player.item_take(self.get_target_item(), order.amount)
            if not item_take_request.success():
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
            self.shop.storage_function.add_item_count(order.amount)  # check for exceptions
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            check_item_request = order.player.item_check(self.shop.target_item_function.get_target_item(), order.amount)
            if not check_item_request.success():
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
        return True

    def log_data(self, order: OrderRequest) -> dict:
        return {
            "amount": order.amount
        }
