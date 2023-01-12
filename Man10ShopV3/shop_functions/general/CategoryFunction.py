from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class CategoryFunction(ShopFunction):
    allowed_shop_type = []

    def set_category(self, name: str):
        return self.set("category", name)

    def get_category(self):
        return self.get("category", "default")