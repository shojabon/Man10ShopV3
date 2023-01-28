from __future__ import annotations

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Man10ShopV3.data_class.Shop import Shop


class TargetItemFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    # variables

    def on_function_init(self):
        self.set_variable("item", ItemStack().get_json(), variable_check=self.on_set_target_item)

    def get_target_item(self) -> ItemStack:
        return ItemStack().from_json(self.get("item"))

    def set_target_item(self, item: ItemStack):
        return self.set("item", item.get_json())

    # =========

    def on_set_target_item(self, shop: Shop, player: Player, new_value):
        if player is None:
            return False
        if shop.storage_function.users_in_storage:
            player.warn_message("倉庫編集中にアイテムを変更することはできません")
            return False
        if not shop.is_admin() and shop.storage_function.get_item_count() != 0:
            player.warn_message("アイテム変更時は在庫が空なくてはいけません")
            return False
        return True

    def perform_action(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "BUY":
            if not self.shop.storage_function.remove_item_count(order.amount):
                order.player.warn_message("内部エラーが発生しました")
                return False
            order.player.item_give(self.get_target_item().type_base64, order.amount)  # check for exceptions ?
        if self.shop.get_shop_type() == "SELL":
            item_take_request = order.player.item_take(self.get_target_item().type_base64, order.amount)
            if not item_take_request.success():
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
            self.shop.storage_function.add_item_count(order.amount)  # check for exceptions
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            check_item_request = order.player.item_check(self.shop.target_item_function.get_target_item().type_base64,
                                                         order.amount)
            if not check_item_request.success():
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
        if self.shop.get_shop_type() == "BUY":
            inventory_space_check_request = order.player.has_inventory_space()
            if not inventory_space_check_request.success():
                order.player.warn_message(inventory_space_check_request.message())
                return False
        return True

    def log_data(self, order: OrderRequest) -> dict:
        return {
            "amount": order.amount
        }
