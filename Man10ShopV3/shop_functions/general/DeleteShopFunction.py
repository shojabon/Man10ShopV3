from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class DeleteShopFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("deleted", False)

    def is_deleted(self):
        return self.get("deleted")

    def sign_information(self, sign_info: list) -> list:
        if self.is_deleted():
            return [
                " ",
                " ",
                " ",
                " ",
            ]