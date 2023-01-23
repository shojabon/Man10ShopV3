import datetime
from typing import Optional, List

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class SetBarterFunction(ShopFunction):
    allowed_shop_type = ["BARTER"]

    def on_function_init(self):
        self.set_variable("required_items", [None, None, None, None, None, None, None, None, None, None, None, None]) # ItemStack Objects
        self.set_variable("result_items", [None]) # ItemStack objects

    def get_required_items(self) -> List[ItemStack]:
        return [ItemStack().from_json(x) if x is not None else None for x in self.get("required_items")]

    def get_result_items(self) -> List[ItemStack]:

        return [ItemStack().from_json(x) if x is not None else None for x in self.get("result_items")]

    # def is_function_enabled(self) -> bool:
    #     if len([x for x in self.get_required_items() if x is not None]) == 0 or self.get_result_items()[0] is None:
    #         return False
    #     return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        required_item_map = {}

        for required_item in [x for x in self.get_required_items() if x is not None]:
            if required_item.type_base64 not in required_item_map:
                required_item_map[required_item.type_base64] = 0
            required_item_map[required_item.type_base64] += required_item.amount
        for required_item in required_item_map.keys():
            if not order.player.item_check(required_item, required_item_map[required_item]).success():
                order.player.warn_message("トレードのためのアイテムが不足してます")
                return False
        return True

    def perform_action(self, order: OrderRequest) -> bool:
        for required_item in [x for x in self.get_required_items() if x is not None]:
            if not order.player.item_take(required_item.type_base64, required_item.amount):
                order.player.warn_message("トレードのためのアイテムが不足してます")
                return False

        order.player.item_give(self.get_result_items()[0].type_base64, self.get_result_items()[0].amount)
        return True

    # temp ?
    def item_count(self, player: Player) -> Optional[int]:
        return 0

    def sign_information(self, sign_info: list) -> list:
        return [
            "",
            " " if self.shop.shop_enabled_function.is_enabled() else "",
            "",
            ""
        ]