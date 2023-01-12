from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class TargetItemFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    # variables

    def get_target_item(self) -> ItemStack:
        default_item = ItemStack()
        return self.get("item", default_item)

    def set_target_item(self, item: ItemStack):
        return self.set("item", item.get_json())

    # =========

    def perform_action(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "BUY":
            if not self.shop.storage_function.remove_item_count(self.get_target_item().amount * order.amount):
                order.player.warn_message("内部エラーが発生しました")
                return False
            order.player.item_give(self.get_target_item(), order.amount) # check for exceptions ?
        if self.shop.get_shop_type() == "SELL":
            if not order.player.item_take(self.get_target_item(), order.amount):
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
            if not self.shop.storage_function.add_item_count(self.get_target_item().amount * order.amount):
                order.player.warn_message("内部エラーが発生しました")
                return False
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            if self.get_target_item().md5_type not in order.player.inventory:
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
            if order.player.inventory[self.get_target_item().md5_type] < order.amount:
                order.player.warn_message("買い取るためのアイテムが不足してます")
                return False
        return True

