import codecs
import hashlib

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class TargetItemFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    # variables

    def on_function_init(self):
        self.set_default("item", ItemStack().base64)
        self.set_default("item_hash", ItemStack().md5)

    def get_target_item(self) -> str:
        return self.get("item")

    def set_target_item(self, item_base64: str):
        return self.set("item", item_base64)

    def get_target_item_hash(self):
        return self.get("item_hash")

    def set_target_item_hash(self, item_hash: str):
        return self.set("item_hash", item_hash)

    # =========

    def perform_action(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "BUY":
            if not self.shop.storage_function.remove_item_count(order.amount):
                order.player.warn_message("内部エラーが発生しました")
                return False
            order.player.item_give(self.get_target_item(), order.amount) # check for exceptions ?
        if self.shop.get_shop_type() == "SELL":
            if not order.player.item_take(self.get_target_item(), order.amount):
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
            if not self.shop.storage_function.add_item_count(order.amount):
                order.player.warn_message("内部エラーが発生しました")
                return False
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            if self.get_target_item_hash() not in order.player.inventory:
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
            if order.player.inventory[self.get_target_item_hash()] < order.amount:
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
        return True

