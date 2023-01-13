from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class PriceFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    # variables
    def on_function_init(self):
        self.set_variable("price", 1000)

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
                order.player.warn_message("現金が不足しています")
                return False

        if self.shop.get_shop_type() == "SELL":
            total_price = self.get_price() * order.amount
            if total_price > self.shop.money_function.get_money() and not self.shop.is_admin():
                order.player.warn_message("ショップ残金不足してます")
                return False
        return True

