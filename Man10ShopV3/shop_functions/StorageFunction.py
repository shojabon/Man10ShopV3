from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class StorageFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    # storage_size: max storage size
    # item_count: item count in storage

    # variables

    def get_storage_size(self):
        return self.get("storage_size", 64 * 9)

    def get_item_count(self):
        return self.get("item_count", 0)

    def set_item_count(self, amount: int):
        return self.set("item_count", amount)

    def add_item_count(self, amount: int):
        return self.set_item_count(self.get_item_count() + amount)

    def remove_item_count(self, amount: int):
        return self.set_item_count(self.get_item_count() - amount)

    # =========

    def item_count(self, order: OrderRequest) -> int:
        if self.shop.is_admin(): return 0
        if self.shop.get_shop_type() == "BUY":
            return self.get_item_count()
        if self.shop.get_shop_type() == "SELL":
            return self.get_storage_size() - self.get_item_count()
        return self.get_storage_size()

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            if order.amount + self.get_item_count() >= self.get_storage_size() and not self.shop.is_admin():
                order.player.warn_message("ショップの倉庫がいっぱいです")
                return False

        if self.shop.get_shop_id() == "BUY":
            if order.amount > self.get_item_count() and not self.shop.is_admin():
                order.player.warn_message("在庫がありません")
                return False
        return True
