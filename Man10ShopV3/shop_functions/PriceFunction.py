from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class StorageFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    # storage_size: max storage size
    # item_count: item count in storage

    # variables

    def get_price(self):
        return self.get("price")

    # =========

    def perform_action(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "BUY":
            total_price = self.get_price() * order.amount
            if not order.player.take_money(total_price):
                # 内部エラーが発生しました
                return False

            self.shop.money_function.set_money(self.shop.money_function.get_money() + total_price)

        if self.shop.get_shop_type() == "SELL":
            total_price = self.get_price() * order.amount
            if not self.shop.money_function.set_money(self.shop.money_function.get_money() - total_price):
                # 内部エラー
                return False
            order.player.give_money(total_price)
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "BUY":
            total_price = self.get_price() * order.amount
            if total_price < order.player.get_balance():
                # 現金が不足しています
                return False

        if self.shop.get_shop_type() == "SELL":
            total_price = self.get_price() * order.amount
            if total_price > self.shop.money_function.get_money() and not self.shop.is_admin():
                # ショップの現金足りない
                return False
        return True

