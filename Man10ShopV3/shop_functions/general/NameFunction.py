from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class NameFunction(ShopFunction):
    allowed_shop_type = []
    def on_function_init(self):
        self.set_variable("name", "ショップ")

    def set_name(self, name: str):
        return self.set("name", name)

    def get_name(self):
        return self.get("name")