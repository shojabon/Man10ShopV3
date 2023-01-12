from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class MoneyFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    def item_count(self, order: OrderRequest) -> int:
        if self.shop.is_admin(): return 0
        if self.shop.get_shop_type() == "SELL":
            if self.shop.get_price() == 0: return super().item_count(order)
            return self.get("money")//self.shop.get_price()
        return super().item_count(order)

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            if self.get("money") < self.shop.get_price() and not self.shop.is_admin():
                # ショップ残金不足してます
                return False
        return True
