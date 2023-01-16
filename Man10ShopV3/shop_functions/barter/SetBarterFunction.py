import datetime
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class SetBarterFunction(ShopFunction):
    allowed_shop_type = ["BARTER"]

    # item data
    # type_base64 str
    # amount int
    # type_md5 str

    # or None

    def on_function_init(self):
        self.set_variable("required_items", [None, None, None, None, None, None, None, None, None, None, None, None])
        self.set_variable("result_items", [None])

    def get_required_items(self):
        return self.get("required_items")

    def get_result_items(self):
        return self.get("result_items")

    def is_function_enabled(self) -> bool:
        if len([x for x in self.get_required_items() if x is not None]) == 0 or self.get_result_items()[0] is None:
            return False
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        for required_item in [x for x in self.get_required_items() if x is not None]:
            if not order.player.item_check(required_item["type_base64"], required_item["amount"]).success():
                order.player.warn_message("トレードのためのアイテムが不足してます")
                return False
        return True

    def perform_action(self, order: OrderRequest) -> bool:
        for required_item in [x for x in self.get_required_items() if x is not None]:
            if not order.player.item_take(required_item["type_base64"], required_item["amount"]):
                order.player.warn_message("トレードのためのアイテムが不足してます")
                return False

        order.player.item_give(self.get_result_items()[0]["type_base64"], self.get_result_items()[0]["amount"])
        return True

    def sign_information(self, sign_info: list) -> list:
        return [
            "§b§lトレードショップ",
            "",
            "",
            ""
        ]

    # temp ?
    def item_count(self, player: Player) -> Optional[int]:
        return 0