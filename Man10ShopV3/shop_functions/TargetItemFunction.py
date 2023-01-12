from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class TargetItemFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    # variables

    def get_target_item(self) -> ItemStack:
        return self.get("item")

    def set_target_item(self, item: ItemStack):
        return self.set("item", item.get_json())

    # =========

    def perform_action(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "BUY":
            if not self.shop.storage_function.remove_item_count(self.get_target_item().amount * order.amount):
                order.player.warn_message("内部エラーが発生しました")
                return False
            # give item to player
        if self.shop.get_shop_type() == "SELL":
            if not self.shop.storage_function.add_item_count(self.get_target_item().amount * order.amount):
                order.player.warn_message("内部エラーが発生しました")
                return False
            # remove item from player
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            pass
            # if player doesn't have enough items return
        return True

